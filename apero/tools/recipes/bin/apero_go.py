#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-27 at 10:56

@author: cook
"""
import argparse
import os
import sys
from typing import Any, Dict

from apero.base import base
from apero.base import drs_base
from apero.core import constants
from apero.core.constants import path_definitions
from apero.core.utils import drs_startup

from apero.core.instruments.default import recipe_definitions as rd

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_go.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in __main__
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
def get_args() -> Dict[str, Any]:
    """
    Apero go should be quick
    :return:
    """
    # get parser
    description = rd.go_recipe.description
    parser = argparse.ArgumentParser(description=description)
    # add the full database
    pargs, pkwargs = rd.go_recipe.proxy_keywordarg('data')
    parser.add_argument(*pargs, **pkwargs)
    # loop around block kinds and add arguments
    for block in path_definitions.BLOCKS:
        # add argument
        pargs, pkwargs = rd.go_recipe.proxy_keywordarg(f'{block.argname}')
        parser.add_argument(*pargs, **pkwargs)
    # parse arguments
    args = parser.parse_args()
    # return as dictionary
    return dict(vars(args))


def main():
    """
    Main function for apero_listing.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # get parameters for this instrument
    params = constants.load()
    # add arguments as inputs (via argparse)
    params['INPUTS'] = get_args()
    # run the __main__ function
    __main__(None, params)


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
    # default value
    props = dict()
    props['path'] = None
    props['chdir'] = False

    storage = dict()
    # ----------------------------------------------------------------------
    # --data option
    # ----------------------------------------------------------------------
    # deal with --data keyword
    if 'DATA' in params['INPUTS']:
        if params['INPUTS']['DATA']:
            value = os.path.dirname(params['DRS_DATA_RAW'])
            # set change dir to True
            if os.path.exists(value):
                props['chdir'] = True
                props['path'] = value
            # append to storage
            storage['Data Directory'] = value

    # ----------------------------------------------------------------------
    # deal with block kind options
    # ----------------------------------------------------------------------
    # loop around block kinds and add arguments
    for block in path_definitions.BLOCKS:
        # check for input key
        if block.argname in params['INPUTS']:
            # deal with --data keyword
            props, storage = get_path(params, storage, props, block.argname,
                                      block.key)

    # ----------------------------------------------------------------------
    # Deal with multiple arguments --> print
    # ----------------------------------------------------------------------
    if len(storage) > 1:
        for item in storage:
            print('{0}: {1}'.format(item, storage[item]))
        multiple = True
    else:
        multiple = False

    # ----------------------------------------------------------------------
    # Change of path
    # ----------------------------------------------------------------------
    # deal with a change of path
    if props['chdir'] and props['path'] is not None and not multiple:
        print(props['path'])

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


def get_path(params, storage, props, input_key, param_key):
    # if is set to True then populate variables
    if params['INPUTS'][input_key]:
        # get the value from params
        value = params[param_key]
        # check path
        if os.path.exists(value):
            props['chdir'] = True
            props['path'] = value
        # update storage
        storage[param_key] = value
    # return props and storage
    return props, storage


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================


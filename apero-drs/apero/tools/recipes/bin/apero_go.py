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
from typing import Any, Dict

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from apero.constants import path_definitions
from apero.instruments.default import recipe_definitions as rd
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_go.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get parameter class
ParamDict = param_functions.ParamDict


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
    # add the all argument
    pargs, pkwargs = rd.go_recipe.proxy_keywordarg('all')
    parser.add_argument(*pargs, **pkwargs)
    # add the setup argument
    pargs, pkwargs = rd.go_recipe.proxy_keywordarg('setup')
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
    Main function for apero_go.py

    """
    # get parameters for this instrument
    params = load_functions.load_config(select.INSTRUMENTS)
    # add arguments as inputs (via argparse)
    params['INPUTS'] = get_args()
    # run the __main__ function
    return __main__(None, params)


def __main__(recipe: None, params: ParamDict) -> Dict[str, Any]:
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe: None, no recipe needed but kept here to match
                   other calls to __main__
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # default value
    props = dict()
    props['path'] = None
    props['chdir'] = False
    # ----------------------------------------------------------------------
    # --setup option
    # ----------------------------------------------------------------------
    if 'setup' in params['INPUTS']:
        if params['INPUTS']['setup']:
            value = os.environ['DRS_UCONFIG']
            print('SETUP: {0}'.format(value))
            return locals()
    # ----------------------------------------------------------------------
    # deal with 'all' argument
    if 'all' in params['INPUTS']:
        if params['INPUTS']['all']:
            for block in path_definitions.BLOCKS:
                params['INPUTS'][f'{block.argname}'] = True
    # ----------------------------------------------------------------------
    # output storage
    storage = dict()
    # ----------------------------------------------------------------------
    # --data option
    # ----------------------------------------------------------------------
    # deal with --data keyword
    if 'data' in params['INPUTS']:
        if params['INPUTS']['data']:
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
    return locals()


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

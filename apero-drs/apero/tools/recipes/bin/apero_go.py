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

import apero as apero_pkg

# Defer heavy APERO imports to runtime to reduce command startup delay.
base = None
load_functions = None
param_functions = None
path_definitions = None
rd = None
select = None

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_go.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
ParamDict = Dict[str, Any]


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
    # add the mysql argument
    pargs, pkwargs = rd.go_recipe.proxy_keywordarg('mysql')
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


def _quick_parse_args() -> Dict[str, bool]:
    """
    Parse fast-path options before loading full APERO runtime.

    :return: dictionary with quick option states
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--setup', action='store_true')
    parser.add_argument('--mysql', action='store_true')
    args, _ = parser.parse_known_args()
    return dict(vars(args))


def _load_runtime_imports() -> None:
    """Load runtime APERO modules only when required."""
    global base, load_functions, param_functions, path_definitions
    global rd, select, ParamDict

    from aperocore.base import base as apero_core_base
    from aperocore.constants import load_functions as apero_load_functions
    from aperocore.constants import param_functions as apero_param_functions
    from apero.constants import path_definitions as apero_path_definitions
    from apero.instruments import select as apero_select
    from apero.instruments.default import recipe_definitions as apero_rd

    base = apero_core_base
    load_functions = apero_load_functions
    param_functions = apero_param_functions
    path_definitions = apero_path_definitions
    rd = apero_rd
    select = apero_select

    ParamDict = param_functions.ParamDict


def main():
    """
    Main function for apero_go.py

    """
    quick_args = _quick_parse_args()

    # Fast-path --setup output without loading full APERO config.
    if quick_args.get('setup', False):
        value = os.environ['DRS_UCONFIG']
        print('SETUP: {0}'.format(value))
        return locals()

    # Fast-path --mysql output without loading instrument constants.
    if quick_args.get('mysql', False):
        from aperocore.base import base as apero_core_base

        dparams = apero_core_base.DPARAMS
        host = dparams['HOST']
        user = dparams['USER']
        passwd = dparams['PASSWD']
        cmd = '>> mysql -h {0} -u {1} -p'
        cmd += 'Pass = {2}'
        print('MYSQL:\n\t' + cmd.format(host, user, passwd))
        return locals()

    # Show immediate feedback before APERO performs heavy module loading.
    print('Loading APERO go runtime...', file=sys.stderr, flush=True)
    _load_runtime_imports()

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
    # --mysql option
    # ----------------------------------------------------------------------
    if 'mysql' in params['INPUTS']:
        if params['INPUTS']['mysql']:
            # load database.yaml
            dparams = base.DPARAMS
            host = dparams['HOST']
            user = dparams['USER']
            passwd = dparams['PASSWD']
            cmd = '>> mysql -h {0} -u {1} -p'
            cmd += 'Pass = {2}'
            print('MYSQL:\n\t' + cmd.format(host, user, passwd))
            return locals()

    # ----------------------------------------------------------------------
    # --setup option
    # ----------------------------------------------------------------------
    if 'setup' in params['INPUTS']:
        if params['INPUTS']['setup']:
            value = os.environ[base.USER_ENV]
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
            value = os.path.dirname(params['PATH.RAW'])
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

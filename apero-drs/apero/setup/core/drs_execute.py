#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-11-19 at 14:33

@author: cook
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from aperocore.base import base
from aperocore.base import resources
from aperocore.constants import load_functions
from aperocore import drs_lang
from aperocore.core import drs_misc
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text

# =============================================================================
# Define variables
# =============================================================================
__PATH__ = Path(__file__).parent.parent.parent
__NAME__ = 'apero.setup.drs_setup.py'
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)
# =============================================================================
# Get variables from info.yaml
# =============================================================================
__version__ = __YAML__['VERSION']
__authors__ = __YAML__['AUTHORS']
__date__ = __YAML__['DATE']
__release__ = __YAML__['RELEASE']

INSTRUMENTS = __YAML__['INSTRUMENTS']
# -----------------------------------------------------------------------------
# get print colours
COLOR = drs_misc.Colors()
# get ParamDict
ParamDict = param_functions.ParamDict
# get execptions
AperoCodedException = drs_log.AperoCodedException
# get WLOG
WLOG = drs_log.wlog
# get textwrap
textentry = drs_lang.textentry
# get the user input function
user_input = drs_text.user_input


# =============================================================================
# Define functions
# =============================================================================
def display_title():
    """
    Print the title of the script
    """
    # set function name
    # _ = display_func('_display_drs_title', __NAME__)
    # get colours
    colors = COLOR
    # create title
    title = colors.okgreen + '* '
    title += colors.RED1 + ' {0} ' + colors.okgreen + '@{1}'
    title += ' (' + colors.BLUE1 + 'V{2}' + colors.okgreen + ')'
    title = title.format('APERO', 'Execute', __version__)
    title += colors.ENDC
    # header
    drs_header = '*' * base.__YAML__['LOG']['DRS_LOG_CHAR_LEN']
    # set function name
    # _ = display_func('_display_title', __NAME__)
    # print and log
    WLOG(None, '', drs_header, wrap=False)
    # add title
    WLOG(None, '', '*\n{0}\n*'.format(title), wrap=False)
    # end header
    WLOG(None, '', drs_header, wrap=False)
    # print logo
    for line in resources.apero_logo():
        WLOG(None, '', colors.RED1 + line + colors.ENDC, wrap=False,
             printonly=True)
    # print and log
    WLOG(None, '', drs_header)


def command_line_args() -> ParamDict:
    # execute description
    description = textentry('EXECUTE_DESCRIPTION')
    # start the parser
    parser = argparse.ArgumentParser(description=description.format(__PATH__))

    # list recipes
    parser.add_argument('--list', action='store_true',
                        help=textentry('EXECUTE_LIST_HELP'))
    parser.add_argument('--xhelp', action='store_true',
                        help=textentry('EXECUTE_XHELP_HELP'))
    parser.add_argument('--dev', action='store_true',
                        help=textentry('EXECUTE_DEV_HELP'))
    parser.add_argument('--debug', action='store_true',
                        help=textentry('EXECUTE_DEBUG_HELP'))
    # get recipe
    parser.add_argument('recipe', nargs='?',
                        help=textentry('EXECUTE_RECIPE_HELP'))

    parser.add_argument('args', nargs=argparse.REMAINDER,
                         help=textentry('EXECUTE_ARGS_HELP'))
    # parse the arguments
    args = parser.parse_args()
    # push into params
    params = ParamDict()
    params['LIST'] = args.list
    params['XHELP'] = args.xhelp
    params['DEV'] = args.dev
    params['DEBUG'] = args.debug
    params['RECIPE'] = args.recipe
    params['ARGS'] = args.args
    # return params
    return params


def get_recipe_list(aparams: ParamDict, attribute: str) -> List[Any]:
    # get instrument class
    instrument = load_functions.load_pconfig(INSTRUMENTS)
    # Get a list of recipes (for instrument + tools)
    recipe_list = list(instrument.RECIPEMOD().recipes)
    # Add in the default recipes
    recipe_list += list(instrument.RECIPEMOD().rd.recipes)
    # deal with bad attribute
    if not hasattr(recipe_list[0], attribute):
        emsg = 'Attribute "{0}" not found in DrsRecipe'
        eargs = [attribute]
        raise AperoCodedException(aparams, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # storage for output
    attribute_list = list(map(lambda x: getattr(x, attribute), recipe_list))
    # return recipes
    return attribute_list


def list_recipes(aparams: ParamDict, rparams: ParamDict):

    name_list = get_recipe_list(aparams, 'name')
    shortname_list = get_recipe_list(aparams, 'shortname')
    type_list = get_recipe_list(aparams, 'recipe_type')
    kind_list = get_recipe_list(aparams, 'recipe_kind')
    # developer mode
    dev = rparams['DEV']
    # -------------------------------------------------------------------------
    # message the list of recipes
    msg = 'List of recipes for {0} instrument:'.format(aparams['INSTRUMENT'])
    # loop around recipes
    for it, shortname in enumerate(shortname_list):
        # deal with not being dev mode and showing admin recipes
        if not dev and 'admin' in kind_list[it]:
            continue
        # only show recipes here
        if 'recipe' in type_list[it]:
            msg_it = '\n\t{0} [{1}]'
            margs = [name_list[it], shortname]
            msg += msg_it.format(*margs)
    WLOG(aparams, 'info', msg)
    # -------------------------------------------------------------------------
    # message the list of tools
    msg = 'List of tools for {0} instrument:'.format(aparams['INSTRUMENT'])
    # loop around tools
    for it, shortname in enumerate(shortname_list):
        # deal with not being dev mode and showing admin recipes
        if 'admin' in kind_list[it]:
            continue
        # only show recipes here
        if 'recipe' not in type_list[it]:
            msg_it = '\n\t{0} [{1}]'
            margs = [name_list[it], shortname]
            msg += msg_it.format(*margs)
    WLOG(aparams, 'info', msg)
    # -------------------------------------------------------------------------
    # message the list of tools
    if dev:
        msg = 'List of dev-tools for {0} instrument:'.format(aparams['INSTRUMENT'])
        # loop around tools
        for it, shortname in enumerate(shortname_list):
            # deal with not being dev mode and showing admin recipes
            if 'admin' not in kind_list[it]:
                continue
            # only show recipes here
            if 'recipe' not in type_list[it]:
                msg_it = '\n\t{0} [{1}]'
                margs = [name_list[it], shortname]
                msg += msg_it.format(*margs)
        WLOG(aparams, 'info', msg)


def run_recipe(aparams: ParamDict, rparams: ParamDict):

    name_list = get_recipe_list(aparams, 'name')
    shortname_list = get_recipe_list(aparams, 'shortname')
    recipe_list = get_recipe_list(aparams, 'main')
    # deal with running help for the recipe
    if rparams['XHELP']:
        rparams['ARGS'] = ['--help']

    # deal with having the shortname instead of the recipe name
    if rparams['RECIPE'] in shortname_list:
        pos = shortname_list.index(rparams['RECIPE'])
        rparams['RECIPE'] = name_list[pos]

    # make sure recipe has .py at the end
    if rparams['RECIPE'] is not None:
        if not rparams['RECIPE'].endswith('.py'):
            rparams['RECIPE'] += '.py'

    # deal with not having the correct recipe
    if rparams['RECIPE'] not in name_list:
        emsg = 'Recipe "{0}" not found in recipe list'
        WLOG(aparams, 'error', emsg.format(rparams['RECIPE']))

    # run the recipe
    msg = 'Running recipe:'
    msg += '\n\t {0} {1}'
    margs = [rparams['RECIPE'], ' '.join(rparams['ARGS'])]
    WLOG(aparams, 'info', msg.format(*margs))

    if not rparams['DEBUG']:
        # push all arguments into sys.argv
        sys.argv = [rparams['RECIPE']] + rparams['ARGS']
        # get position
        pos = name_list.index(rparams['RECIPE'])
        # run the recipe
        recipe_list[pos]()

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

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
from aperocore import drs_lang
from aperocore.core import drs_misc
from aperocore.constants import param_functions
from aperocore.constants import load_functions
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
    title = title.format('APERO', 'Setup', __version__)
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
    params['RECIPE'] = args.recipe
    params['ARGS'] = args.args
    # return params
    return params



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

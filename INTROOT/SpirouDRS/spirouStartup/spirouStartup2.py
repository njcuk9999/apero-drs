#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 18:05

@author: cook
"""
from __future__ import division
import numpy as np
import os
import sys
import code
from collections import OrderedDict

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

from . import spirouRecipe
from . import recipes

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouStartup.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# get param dict
ParamDict = spirouConfig.ParamDict
# get the config error
ConfigError = spirouConfig.ConfigError
# get recipes
RECIPES = recipes.recipes
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def input_setup(name):
    func_name = __NAME__ + '.setup()'
    # quietly load DRS parameters (for setup)
    drs_params = get_drs_params(__NAME__, quiet=True)
    # find recipe
    found_recipe = None
    for recipe in RECIPES:
        if recipe.name == name:
            found_recipe = recipe
    if found_recipe is None:
        raise ValueError('No recipe named {0}'.format(name))
    # make the recipe
    found_recipe.make()
    desc = found_recipe.description
    # add params to drs_params
    drs_params['recipe'] = dict()
    drs_params.set_source('recipe', func_name)
    # load properties into recipe dictionary
    drs_params['recipe']['name'] = name
    drs_params['recipe']['outputdir'] = found_recipe.outputdir
    drs_params['recipe']['inputdir'] = found_recipe.inputdir
    drs_params['recipe']['inputtype'] = found_recipe.inputtype
    # set up storage for arguments
    parser = spirouRecipe.DRSArgumentParser(drs_params, description=desc)
    # add arguments
    for arg in found_recipe.arg_list:
        parser.add_argument(arg[0], **arg[1])
    # get params
    params = vars(parser.parse_args())
    # return arguments
    return params


def get_drs_params(recipe, quiet=False):
    func_name = __NAME__ + '.run_begin()'
    constants_name = 'spirouConfig.Constants'
    # Clean WLOG
    WLOG.clean_log()
    # Get config parameters from primary file
    try:
        drs_params, warn_messages = spirouConfig.ReadConfigFile()
    except ConfigError as e:
        WLOG(e.level, DPROG, e.message)
        drs_params, warn_messages = None, []
    # log warning messages
    if len(warn_messages) > 0:
        WLOG('warning', DPROG, warn_messages)
    # set recipe name
    drs_params['RECIPE'] = recipe.split('.py')[0]
    drs_params.set_source('RECIPE', func_name)
    # get variables from spirouConst
    drs_params['DRS_NAME'] = spirouConfig.Constants.NAME()
    drs_params['DRS_VERSION'] = spirouConfig.Constants.VERSION()
    drs_params.set_sources(['DRS_NAME', 'DRS_VERSION'], constants_name)

    # get program name
    drs_params['PROGRAM'] = spirouConfig.Constants.PROGRAM(drs_params)
    drs_params.set_source('program', func_name)
    # get the logging option
    drs_params['LOG_OPT'] = drs_params['PROGRAM']
    drs_params.set_source('LOG_OPT', func_name)

    # check input parameters
    drs_params = spirouConfig.CheckCparams(drs_params)

    # if DRS_INTERACTIVE is not True then DRS_PLOT should be turned off too
    if not drs_params['DRS_INTERACTIVE']:
        drs_params['DRS_PLOT'] = 0

    # set up array to store inputs/outputs
    drs_params['INPUTS'] = OrderedDict()
    drs_params['OUTPUTS'] = OrderedDict()
    source = recipe + '.main() + ' + func_name
    drs_params.set_sources(['INPUTS', 'OUTPUTS'], source)
    # -------------------------------------------------------------------------
    # load ICDP config file
    logthis = not quiet
    drs_params = load_other_config_file(drs_params, 'ICDP_NAME', required=True,
                                        logthis=logthis)
    # load keywords
    try:
        cparams, warnlogs = spirouConfig.GetKeywordArguments(drs_params)
        # print warning logs
        for warnlog in warnlogs:
            WLOG('warning', DPROG, warnlog)
    except spirouConfig.ConfigError as e:
        WLOG(e.level, DPROG, e.message)

    # return drs parameters
    return drs_params


# =============================================================================
# Worker functions
# =============================================================================
def load_other_config_file(p, key, logthis=True, required=False):
    """
    Load a secondary configuration file from p[key] with wrapper to deal
    with ConfigErrors (pushed to WLOG)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                key: "key" defined in call

    :param key: string, the key in "p" storing the location of the secondary
                configuration file
    :param logthis: bool, if True loading of this config file is logged to
                    screen/log file
    :param required: bool, if required is True then the secondary config file
                     is required for the DRS to run and a ConfigError is raised
                     (program exit)

    :return p: parameter, dictionary, the updated parameter dictionary with
               the secondary configuration files loaded into it as key/value
               pairs
    """
    # try to load config file from file
    try:
        pp, lmsgs = spirouConfig.LoadConfigFromFile(p, key, required=required,
                                                    logthis=logthis)
    except spirouConfig.ConfigError as e:
        WLOG(e.level, p['LOG_OPT'], e.message)
        pp, lmsgs = ParamDict(), []

    # log messages caught in loading config file
    if len(lmsgs) > 0:
        WLOG('', DPROG, lmsgs)
    # return parameter dictionary
    return pp


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

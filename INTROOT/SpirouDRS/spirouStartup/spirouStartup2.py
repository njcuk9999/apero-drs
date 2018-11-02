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
from . import recipes_spirou

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
RECIPES = recipes_spirou.recipes
# -----------------------------------------------------------------------------
# define the print/log header divider
HEADER = ' *****************************************'


# =============================================================================
# Define functions
# =============================================================================
def input_setup(name, fkwargs=None, quiet=False):
    func_name = __NAME__ + '.setup()'
    # deal with no keywords
    if fkwargs is None:
        fkwargs = dict()
    # quietly load DRS parameters (for setup)
    drs_params = get_drs_params(name, quiet=True)
    # display
    if not quiet:
        # display title
        display_drs_title(drs_params)
        # display initial parameterisation
        display_initial_parameterisation(drs_params)
        # display system info (log only)
        display_system_info()
    # -------------------------------------------------------------------------
    # Deal with obtaining and understanding command-line/function- call inputs
    # -------------------------------------------------------------------------
    # find recipe
    recipe = find_recipe(name)
    # add params to drs_params
    drs_params['RECIPE'] = dict()
    drs_params.set_source('RECIPE', func_name)
    # load properties into recipe dictionary
    drs_params['RECIPE']['name'] = name
    drs_params['RECIPE']['args'] = recipe.args
    drs_params['RECIPE']['kwargs'] = recipe.kwargs
    # drs_params['RECIPE']['outputdir'] = recipe.outputdir.upper()
    drs_params['RECIPE']['inputdir'] = recipe.inputdir.upper()
    # drs_params['RECIPE']['inputtype'] = recipe.inputtype.upper()
    # set up storage for arguments
    desc = recipe.description
    parser = spirouRecipe.DRSArgumentParser(drs_params, description=desc)
    # deal with function call
    recipe.parse_args(fkwargs)
    # add arguments
    for rarg in recipe.args:
        # extract out name and kwargs from rarg
        rname = recipe.args[rarg].names
        rkwargs = recipe.args[rarg].props
        # parse into parser
        parser.add_argument(*rname, **rkwargs)
    # add keyword arguments
    for rarg in recipe.kwargs:
        # extract out name and kwargs from rarg
        rname = recipe.kwargs[rarg].names
        rkwargs = recipe.kwargs[rarg].props
        # parse into parser
        parser.add_argument(*rname, **rkwargs)
    # add special arguments
    for rarg in recipe.specialargs:
        # extract out name and kwargs from rarg
        rname = recipe.specialargs[rarg].names
        rkwargs = recipe.specialargs[rarg].props
        # parse into parser
        parser.add_argument(*rname, **rkwargs)
    # get params
    params = vars(parser.parse_args(args=recipe.str_arg_list))
    del parser
    # add to DRS parameters
    drs_params['INPUT'] = params
    # return arguments
    return drs_params


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
# Define display functions
# =============================================================================
def display_drs_title(p):
    """
    Display title for this execution

    :param p: dictionary, parameter dictionary

    :return None:
    """
    # create title
    title = ' * {DRS_NAME} @(#) Geneva Observatory ({DRS_VERSION})'.format(**p)

    # Log title
    display_title(title)

    if p['DRS_DEBUG'] == 42:
        display_ee()


def display_title(title):
    """
    Display any title between HEADER bars via the WLOG command

    :param title: string, title string

    :return None:
    """
    # Log title
    WLOG('', '', HEADER)
    WLOG('', '',
         '{0}'.format(title))
    WLOG('', '', HEADER)


def display_ee():
    bcolors = spirouConfig.Constants.BColors

    # noinspection PyPep8
    logo = ['',
            '      `-+syyyso:.   -/+oossssso+:-`   `.-:-`  `...------.``                                 ',
            '    `ohmmmmmmmmmdy: +mmmmmmmmmmmmmy- `ydmmmh: sdddmmmmmmddho-                               ',
            '   `ymmmmmdmmmmmmmd./mmmmmmhhhmmmmmm-/mmmmmmo ymmmmmmmmmmmmmmo                              ',
            '   /mmmmm:.-:+ydmm/ :mmmmmy``.smmmmmo.ydmdho` ommmmmhsshmmmmmm.      ```                    ',
            '   ommmmmhs+/-..::  .mmmmmmoshmmmmmd- `.-::-  +mmmmm:  `hmmmmm`  `-/+ooo+:.   .:::.   .:/// ',
            '   .dmmmmmmmmmdyo.   mmmmmmmmmmmddo. oyyyhm/  :mmmmmy+osmmmmms  `osssssssss+` /sss-   :ssss ',
            '    .ohdmmmmmmmmmmo  dmmmmmdo+/:.`   ymmmmm/  .mmmmmmmmmmmmms`  +sss+..-ossso`+sss-   :ssss ',
            '   --.`.:/+sdmmmmmm: ymmmmmh         ymmmmm/   mmmmmmmmmddy-    ssss`   :ssss.osss.   :ssss ',
            '  +mmmhs/-.-smmmmmm- ommmmmm`        hmmmmm/   dmmmmm/sysss+.  `ssss-  `+ssss`osss`   :ssss ',
            ' -mmmmmmmmmmmmmmmms  /mmmmmm.        hmmmmm/   ymmmmm``+sssss/` /sssso+sssss- +sss:` .ossso ',
            ' -sdmmmmmmmmmmmmdo`  -mmmmmm/        hmmmmm:   smmmmm-  -osssss/`-osssssso/.  -sssssosssss+ ',
            '    ./osyhhhyo+-`    .mmmddh/        sddhhy-   /mdddh-    -//::-`  `----.      `.---.``.--. ',
            '']

    for line in logo:
        WLOG('', '', bcolors.FAIL + line + bcolors.ENDC, wrap=False)


def display_initial_parameterisation(p):
    """
    Display initial parameterisation for this execution

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_DATA_RAW: string, the directory that the raw data should
                              be saved to/read from
                DRS_DATA_REDUC: string, the directory that the reduced data
                                should be saved to/read from
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from
                DRS_DATA_MSG: string, the directory that the log messages
                              should be saved to
                PRINT_LEVEL: string, Level at which to print, values can be:
                                  'all' - to print all events
                                  'info' - to print info/warning/error events
                                  'warning' - to print warning/error events
                                  'error' - to print only error events
                LOG_LEVEL: string, Level at which to log, values can be:
                                  'all' - to print all events
                                  'info' - to print info/warning/error events
                                  'warning' - to print warning/error events
                                  'error' - to print only error events
                DRS_PLOT: bool, Whether to plot (True to plot)
                DRS_USED_DATE: string, the DRS USED DATE (not really used)
                DRS_DATA_WORKING: (optional) string, the temporary working
                                  directory
                DRS_INTERACTIVE: bool, True if running in interactive mode.
                DRS_DEBUG: int, Whether to run in debug mode
                                0: no debug
                                1: basic debugging on errors
                                2: recipes specific (plots and some code runs)

    :return None:
    """
    # Add initial parameterisation
    WLOG('', '', '(dir_data_raw)      DRS_DATA_RAW={DRS_DATA_RAW}'.format(**p))
    WLOG('', '', '(dir_data_reduc)    DRS_DATA_REDUC={DRS_DATA_REDUC}'
                 ''.format(**p))
    WLOG('', '', '(dir_drs_config)    DRS_CONFIG={DRS_CONFIG}'.format(**p))
    WLOG('', '', '(dir_drs_uconfig)   DRS_UCONFIG={DRS_UCONFIG}'.format(**p))
    WLOG('', '', '(dir_calib_db)      DRS_CALIB_DB={DRS_CALIB_DB}'.format(**p))
    WLOG('', '', '(dir_data_msg)      DRS_DATA_MSG={DRS_DATA_MSG}'.format(**p))
    # WLOG('', '', ('(print_log)         DRS_LOG={DRS_LOG}         '
    #               '%(0: minimum stdin-out logs)').format(**p))
    WLOG('', '', ('(print_level)       PRINT_LEVEL={PRINT_LEVEL}         '
                  '%(error/warning/info/all)').format(**p))
    WLOG('', '', ('(log_level)         LOG_LEVEL={LOG_LEVEL}         '
                  '%(error/warning/info/all)').format(**p))
    WLOG('', '', ('(plot_graph)        DRS_PLOT={DRS_PLOT}            '
                  '%(def/undef/trigger)').format(**p))
    WLOG('', '', ('(used_date)         DRS_USED_DATE={DRS_USED_DATE}'
                  '').format(**p))
    if p['DRS_DATA_WORKING'] is None:
        WLOG('', '', ('(working_dir)       DRS_DATA_WORKING is not set, '
                      'running on-line mode'))
    else:
        WLOG('', '', ('(working_dir)       DRS_DATA_WORKING={DRS_DATA_WORKING}'
                      '').format(**p))
    if p['DRS_INTERACTIVE'] == 0:
        WLOG('', '', ('                    DRS_INTERACTIVE is not set, '
                      'running on-line mode'))
    else:
        WLOG('', '', '                    DRS_INTERACTIVE is set')
    if p['DRS_DEBUG'] > 0:
        WLOG('', '', ('                    DRS_DEBUG is set, debug mode level'
                      ':{DRS_DEBUG}').format(**p))


# noinspection PyListCreation
def display_system_info(logonly=True, return_message=False):
    """
    Display system information via the WLOG command

    :param logonly: bool, if True will only display in the log (not to screen)
                    default=True, if False prints to both log and screen

    :param return_message: bool, if True returns the message to the call, if
                           False logs the message using WLOG

    :return None:
    """
    messages = [HEADER]
    messages.append(" * System information:")
    messages.append(HEADER)
    messages = sort_version(messages)
    messages.append("    Path = \"{0}\"".format(sys.executable))
    messages.append("    Platform = \"{0}\"".format(sys.platform))
    for it, arg in enumerate(sys.argv):
        messages.append("    Arg {0} = \"{1}\"".format(it + 1, arg))
    messages.append(HEADER)
    if return_message:
        return messages
    else:
        # return messages for logger
        WLOG('', '', messages, logonly=logonly)



# =============================================================================
# Worker functions
# =============================================================================
def find_recipe(name):
    found_recipe = None
    for recipe in RECIPES:
        if recipe.name == name:
            found_recipe = recipe
    if found_recipe is None:
        raise ValueError('No recipe named {0}'.format(name))
    # return
    return found_recipe


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


def sort_version(messages=None):
    """
    Obtain and sort version info

    :param messages: list of strings or None, if defined is a list of messages
                     that version_info is added to, else new list of strings
                     is created

    :return messages: list of strings updated or created (if messages is None)
    """
    # deal with no messages
    if messages is None:
        messages = []
    # get version info
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro

    version = '{0}.{1}.{2}'.format(major, minor, micro)

    # add version info to messages
    messages.append('    Python version = {0}'.format(version))

    # add distribution if possible
    try:
        build = sys.version.split('|')[1].strip()
        messages.append('    Python distribution = {0}'.format(build))
    except IndexError:
        pass

    # add date information if possible
    try:
        date = sys.version.split('(')[1].split(')')[0].strip()
        messages.append('    Distribution date = {0}'.format(date))
    except IndexError:
        pass

    # add Other info information if possible
    try:
        other = sys.version.split('[')[1].split(']')[0].strip()
        messages.append('    Dist Other = {0}'.format(other))
    except IndexError:
        pass

    # return updated messages
    return messages


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

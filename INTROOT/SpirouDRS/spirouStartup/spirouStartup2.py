#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 18:05

@author: cook
"""
from __future__ import division
import sys
import time

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
    # set up process id
    pid = assign_pid()
    # Clean WLOG
    WLOG.clean_log(pid)
    # find recipe
    recipe = find_recipe(name)
    # quietly load DRS parameters (for setup)
    recipe.get_drs_params(quiet=True, pid=pid)
    # display
    if not quiet:
        # display title
        display_drs_title(recipe.drs_params)
        # display initial parameterisation
        display_initial_parameterisation(recipe.drs_params)
        # display system info (log only)
        display_system_info(recipe.drs_params)
    # -------------------------------------------------------------------------
    # interface between "recipe", "fkwargs" and command line (via argparse)
    input_parameters = spirouRecipe.recipe_setup(recipe, fkwargs)
    # -------------------------------------------------------------------------
    # deal with options from input_parameters
    input_parameters = option_manager(recipe, input_parameters)
    # -------------------------------------------------------------------------
    # add to DRS parameters
    drs_params = recipe.drs_params
    drs_params['INPUT'] = input_parameters
    drs_params.set_source('INPUT', func_name)
    # push values of keys matched in input_parameters into drs_parameters
    for key in input_parameters.keys():
        if key in drs_params:
            drs_params[key] = input_parameters[key]
            drs_params.set_source(key, func_name)
    # update default params
    spirouConfig.Constants.UPDATE_PP(drs_params)
    # return arguments
    return drs_params


# =============================================================================
# option arguments
# =============================================================================
def option_manager(recipe, input_parameters):
    """
    Takes all the optional parameters and deals with them.

    :param recipe:
    :param input_parameters:
    :return:
    """
    # get drs params
    params = recipe.drs_params
    # loop around options
    for key in recipe.kwargs:
        # get keyword argument
        kwarg = recipe.kwargs[key]
        # make sure kind == 'kwarg
        if kwarg.kind != 'kwarg':
            continue
        # check that kwarg is in input_parameters
        if kwarg.name not in input_parameters:
            eargs = [kwarg.name, recipe.name]
            emsg = 'Cannot find input "{0}" for recipe "{1}"'
            kwarg.exception(emsg.format(*eargs))
        # check that kwarg is None (should be None if we need to change it)
        if input_parameters[kwarg.name] is not None:
            # if we have the value we should pipe it into default_ref
            #  i.e. the value in the parameters file
            if kwarg.default_ref is not None:
                param_key = kwarg.default_ref
                value = input_parameters[kwarg.name]
            else:
                continue
        # check that default is None
        elif kwarg.default is not None:
            value, param_key = kwarg.default, None
        # else check that we have default_ref
        elif kwarg.default_ref is None:
            eargs = [kwarg.name, recipe.name]
            emsg = '"default_ref" is unset for "{0}" for recipe "{1}"'
            kwarg.exception(emsg.format(*eargs))
            value, param_key = None, None
        # else check that default_ref is in drs_params (i.e. defined in a
        #   constant file)
        elif kwarg.default_ref not in params:
            eargs = [kwarg.default_ref, kwarg.name, recipe.name]
            emsg = ('"default_ref"="{0}" not found in constant params for '
                    ' "{1}" for recipe "{2}"')
            kwarg.exception(emsg.format(*eargs))
            value, param_key = None, None
        # else we have all we need to reset the value
        else:
            value = params[kwarg.default_ref]
            param_key = kwarg.default_ref
        # if we have reached this point then set value
        input_parameters[kwarg.name] = value
        if param_key is not None:
            input_parameters[kwarg.default_ref] = value

    # return the parameters
    return input_parameters


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
    title = ' * {DRS_NAME} @{PID} ({DRS_VERSION})'.format(**p)

    # Log title
    display_title(p, title)

    if p['DRS_DEBUG'] == 42:
        display_ee(p)


def display_title(p, title):
    """
    Display any title between HEADER bars via the WLOG command

    :param title: string, title string

    :return None:
    """
    # Log title
    WLOG(p, '', HEADER)
    WLOG(p, '', '{0}'.format(title))
    WLOG(p, '', HEADER)


def display_ee(p):
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
        WLOG(p, '', bcolors.FAIL + line + bcolors.ENDC, wrap=False)


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
    WLOG(p, '', '(dir_data_raw)      DRS_DATA_RAW={DRS_DATA_RAW}'.format(**p))
    WLOG(p, '', '(dir_data_reduc)    DRS_DATA_REDUC={DRS_DATA_REDUC}'
                ''.format(**p))
    WLOG(p, '', '(dir_drs_config)    DRS_CONFIG={DRS_CONFIG}'.format(**p))
    WLOG(p, '', '(dir_drs_uconfig)   DRS_UCONFIG={DRS_UCONFIG}'.format(**p))
    WLOG(p, '', '(dir_calib_db)      DRS_CALIB_DB={DRS_CALIB_DB}'.format(**p))
    WLOG(p, '', '(dir_tellu_db)      DRS_TELLU_DB={DRS_TELLU_DB}'.format(**p))
    WLOG(p, '', '(dir_data_msg)      DRS_DATA_MSG={DRS_DATA_MSG}'.format(**p))
    # WLOG(p, '', ('(print_log)         DRS_LOG={DRS_LOG}         '
    #               '%(0: minimum stdin-out logs)').format(**p))
    WLOG(p, '', ('(print_level)       PRINT_LEVEL={PRINT_LEVEL}         '
                 '%(error/warning/info/all)').format(**p))
    WLOG(p, '', ('(log_level)         LOG_LEVEL={LOG_LEVEL}         '
                 '%(error/warning/info/all)').format(**p))
    WLOG(p, '', ('(plot_graph)        DRS_PLOT={DRS_PLOT}            '
                 '%(def/undef/trigger)').format(**p))
    if p['DRS_DATA_WORKING'] is None:
        WLOG(p, '', ('(working_dir)       DRS_DATA_WORKING is not set, '
                     'running on-line mode'))
    else:
        WLOG(p, '', ('(working_dir)       DRS_DATA_WORKING={DRS_DATA_WORKING}'
                     '').format(**p))
    if p['DRS_INTERACTIVE'] == 0:
        WLOG(p, '', ('                    DRS_INTERACTIVE is not set, '
                     'running on-line mode'))
    else:
        WLOG(p, '', '                    DRS_INTERACTIVE is set')
    if p['DRS_DEBUG'] > 0:
        WLOG(p, '', ('                    DRS_DEBUG is set, debug mode level'
                     ':{DRS_DEBUG}').format(**p))


def display_system_info(p, logonly=True, return_message=False):
    """
    Display system information via the WLOG command

    :param logonly: bool, if True will only display in the log (not to screen)
                    default=True, if False prints to both log and screen

    :param return_message: bool, if True returns the message to the call, if
                           False logs the message using WLOG

    :return None:
    """
    # noinspection PyListCreation
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
        WLOG(p, '', messages, logonly=logonly)


# =============================================================================
# Worker functions
# =============================================================================
def assign_pid():
    return 'PID-{0:020d}'.format(int(time.time() * 1e7))


def find_recipe(name):
    found_recipe = None
    for recipe in RECIPES:
        if recipe.name == name:
            found_recipe = recipe
    if found_recipe is None:
        raise ValueError('No recipe named {0}'.format(name))
    # return
    return found_recipe


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

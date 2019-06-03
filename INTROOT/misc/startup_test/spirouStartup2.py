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
import sys
import os
import time
import code
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage

from misc.startup_test import spirouRecipe, recipes_spirou, spirouFile

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
HEADER = spirouConfig.Constants.HEADER()


# =============================================================================
# Define functions
# =============================================================================
def input_setup(name=None, fkwargs=None, quiet=False):
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
    # need to set debug mode now
    recipe = set_debug_from_input(recipe, fkwargs)
    # do not need to display if we have special keywords
    quiet = special_keys_present(recipe, quiet, fkwargs)
    # -------------------------------------------------------------------------
    # display
    if not quiet:
        # display title
        display_drs_title(recipe.drs_params)
    # -------------------------------------------------------------------------
    # interface between "recipe", "fkwargs" and command line (via argparse)
    recipe.recipe_setup(fkwargs)
    # -------------------------------------------------------------------------
    # deal with options from input_parameters
    recipe.option_manager()
    # update default params
    spirouConfig.Constants.UPDATE_PP(recipe.drs_params)
    # -------------------------------------------------------------------------
    # display
    if not quiet:
        # display initial parameterisation
        if recipe.drs_params['DRS_DEBUG'] == 42:
            display_ee(recipe.drs_params)
        # display initial parameterisation
        display_initial_parameterisation(recipe.drs_params)
        # display system info (log only)
        display_system_info(recipe.drs_params)
        # print out of the parameters used
        display_run_time_arguments(recipe, fkwargs)
    # -------------------------------------------------------------------------
    # return arguments
    return recipe, recipe.drs_params


def get_params(**kwargs):
    """
    Wrapper for input_setup

    :return p: parameter dictionary
    """
    _, params = input_setup(None, quiet=True)
    # overwrite parameters with kwargs
    for kwarg in kwargs:
        params[kwarg] = kwargs[kwarg]
    # return parameters
    return params


def main_end_script(p, outputs='reduced'):
    # func_name = __NAME__ + '.main_end_script()'

    if outputs == 'pp':
        # index outputs to pp dir
        index_pp(p)
    elif outputs == 'reduced':
        # index outputs to reduced dir
        index_outputs(p)
    # log end message
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG(p, 'info', wmsg.format(p['PROGRAM']))
    # add the logger messsages to p
    p = WLOG.output_param_dict(p)
    # finally clear out the log in WLOG
    WLOG.clean_log(p['PID'])
    # return p
    return p


# noinspection PyProtectedMember
def exit_script(ll, has_plots=True):
    """
    Exit script for handling interactive endings to sessions (if DRS_PLOT is
    active)

    :param ll: dict, the local variables
    :param has_plots: bool, if True looks for and deal with having plots
                      (i.e. asks the user to close or closest automatically),
                      if False no plot windows are assumed to be open

    :return None:
    """
    # get parameter dictionary of constants (or create it)
    if 'p' in ll:
        p = ll['p']
    else:
        p = OrderedDict()
    # make sure we have DRS_PLOT
    if 'DRS_PLOT' not in p:
        p['DRS_PLOT'] = 0
    # make sure we have DRS_INTERACTIVE
    if 'DRS_INTERACTIVE' not in p:
        p['DRS_INTERACTIVE'] = 1
    # make sure we have log_opt
    if 'log_opt' not in p:
        p['LOG_OPT'] = sys.argv[0]
    # if DRS_INTERACTIVE is False just return 0
    if not p['DRS_INTERACTIVE']:
        # print('Interactive mode off')
        return 0
    # find whether user is in ipython or python
    if find_ipython():
        kind = 'ipython'
    else:
        kind = 'python'
    # log message
    wmsg = 'Press "Enter" to exit or [Y]es to continue in {0}'
    WLOG(p, '', '')
    WLOG(p, '', HEADER, printonly=True)
    WLOG(p, 'warning', wmsg.format(kind), printonly=True)
    WLOG(p, '', HEADER, printonly=True)
    # deal with python 2 / python 3 input method
    if sys.version_info.major < 3:
        # noinspection PyUnresolvedReferences
        uinput = raw_input('')  # note python 3 wont find this!
    else:
        uinput = input('')

    # if yes or YES or Y or y then we need to continue in python
    # this may require starting an interactive session
    if 'Y' in uinput.upper():
        # if user in ipython we need to try opening ipython
        if kind == 'ipython':
            # noinspection PyBroadException
            try:
                from IPython import embed
                # this is only to be used in this situation and should not
                # be used in general
                locals().update(ll)
                embed()
            except Exception:
                pass
        if not find_interactive():
            # add some imports to locals
            ll['np'], ll['plt'], ll['WLOG'] = np, spirouCore.sPlt.plt, WLOG
            ll['os'], ll['sys'], ll['ParamDict'] = os, sys, ParamDict
            # run code
            code.interact(local=ll)
    # if "No" and not interactive quit python/ipython
    elif not find_interactive():
        # noinspection PyProtectedMember
        os._exit(0)
    # if interactive ask about closing plots
    if find_interactive() and has_plots:
        # deal with closing plots
        wmsg = 'Close plots? [Y]es or [N]o?'
        WLOG(p, '', HEADER, printonly=True)
        WLOG(p, 'warning', wmsg.format(kind), printonly=True)
        WLOG(p, '', HEADER, printonly=True)
        # deal with python 2 / python 3 input method
        if sys.version_info.major < 3:
            # noinspection PyUnresolvedReferences
            uinput = raw_input('')  # note python 3 wont find this!
        else:
            uinput = input('')
        # if yes close all plots
        if 'Y' in uinput.upper():
            # close any open plots properly
            spirouCore.sPlt.closeall()


# =============================================================================
# Define display functions
# =============================================================================
def special_keys_present(recipe, quiet, fkwargs):
    """
    Decides whether displaying is necessary based on whether we have special
    keys in fkwargs or sys.argv (input from command line)

    :param recipe: DrsRecipe instance, the recipe to act on
    :param fkwargs: dictionary, the input keywords from python call to recipe
    :param quiet: bool, the current status of quiet flag (True or False)

    :return quiet: bool, the updated status of quiet flag
    """
    # get the special keys
    skeys = get_recipe_keys(recipe.specialargs, add=['--help', '-h'])
    # see if we have a key
    if len(skeys) > 0:
        for skey in skeys:
            found_key = search_for_key(skey, fkwargs)
            if found_key:
                quiet = True
    # return the updated quiet flag
    return quiet


def display_drs_title(p):
    """
    Display title for this execution

    :param p: dictionary, parameter dictionary

    :return None:
    """
    # get colours
    colors = spirouConfig.Constants.Colors()

    # create title
    title = ' * '
    title += colors.RED1 + ' {DRS_NAME} ' + colors.okgreen + '@{PID}'
    title += ' (' + colors.BLUE1 + 'V{DRS_VERSION}' + colors.okgreen + ')'
    title += colors.ENDC
    title = title.format(**p)

    # Log title
    display_title(p, title)


def display_title(p, title):
    """
    Display any title between HEADER bars via the WLOG command

    :param p: dictionary, parameter dictionary
    :param title: string, title string

    :return None:
    """
    # Log title
    WLOG(p, '', HEADER)
    WLOG(p, '', '{0}'.format(title), wrap=False)
    WLOG(p, '', HEADER)


def display_ee(p):
    # get colours
    colors = spirouConfig.Constants.Colors()

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
        WLOG(p, '', colors.RED1 + line + colors.ENDC, wrap=False)
    WLOG(p, '', HEADER)


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
    wmsgs = ['\tDRS_DATA_RAW={DRS_DATA_RAW}'.format(**p),
             '\tDRS_DATA_REDUC={DRS_DATA_REDUC}'.format(**p),
             '\tDRS_CONFIG={DRS_CONFIG}'.format(**p),
             '\tDRS_UCONFIG={DRS_UCONFIG}'.format(**p),
             '\tDRS_CALIB_DB={DRS_CALIB_DB}'.format(**p),
             '\tDRS_TELLU_DB={DRS_TELLU_DB}'.format(**p),
             '\tDRS_DATA_MSG={DRS_DATA_MSG}'.format(**p),
             '\tPRINT_LEVEL={PRINT_LEVEL}'.format(**p),
             '\tLOG_LEVEL={LOG_LEVEL}'.format(**p),
             '\tDRS_PLOT={DRS_PLOT}'.format(**p)]
    if p['DRS_DATA_WORKING'] is None:
        wmsgs.append('\tDRS_DATA_WORKING is not set, running on-line mode')
    else:
        wmsgs.append('\tDRS_DATA_WORKING={DRS_DATA_WORKING}'.format(**p))
    if p['DRS_INTERACTIVE'] == 0:
        wmsgs.append('\tDRS_INTERACTIVE is not set, running on-line mode')
    else:
        wmsgs.append('\tDRS_INTERACTIVE is set')
    if p['DRS_DEBUG'] > 0:
        wmsgs.append('\tDRS_DEBUG is set, debug mode level:{DRS_DEBUG}'
                     ''.format(**p))
    # log to screen and file
    WLOG(p, 'info', 'DRS Setup:')
    WLOG(p, 'info', wmsgs, wrap=False)
    WLOG(p, '', HEADER)


def display_system_info(p, logonly=True, return_message=False):
    """
    Display system information via the WLOG command

    :param p: dictionary, parameter dictionary
    :param logonly: bool, if True will only display in the log (not to screen)
                    default=True, if False prints to both log and screen

    :param return_message: bool, if True returns the message to the call, if
                           False logs the message using WLOG

    :return None:
    """
    # noinspection PyListCreation
    messages = []
    if return_message:
        messages.append(HEADER)
        messages.append(" * System information:")
        messages.append(HEADER)
    messages = sort_version(messages)
    messages.append("    Path = \"{0}\"".format(sys.executable))
    messages.append("    Platform = \"{0}\"".format(sys.platform))
    for it, arg in enumerate(sys.argv):
        messages.append("    Arg {0} = \"{1}\"".format(it + 1, arg))
    if return_message:
        messages.append(HEADER)
        return messages
    else:
        # return messages for logger
        WLOG(p, '', HEADER, logonly=logonly)
        WLOG(p, 'info', " * System information:", logonly=logonly)
        WLOG(p, '', HEADER, logonly=logonly)
        WLOG(p, '', messages, logonly=logonly)
        WLOG(p, '', HEADER, logonly=logonly)


def display_arg_setup(p):
    """
    Display for setting up and checking arguments
    :param p: dictionary, parameter dictionary
    :return None:
    """
    WLOG(p, '', ' Setting up and checking arguments')
    WLOG(p, '', HEADER)


def display_run_time_arguments(recipe, fkwargs=None):
    """
    Display for arguments used (got from p['INPUT'])

    :param p: dictionary, parameter dictionary
        Must contain at least:
            INPUT: parameters obtained for this recipe
    :return None:
    """
    log_strings = []
    # get parameters
    p = recipe.drs_params
    # get special keys
    skeys = get_recipe_keys(recipe.specialargs, remove_prefix='-',
                            add=['--help', '-h'])
    pkeys = keys_present(recipe, fkwargs, remove_prefix='-')
    # loop around inputs
    for argname in p['INPUT']:
        # if we have a special input ignore
        if argname in skeys:
            continue
        # if keys aren't present in sys.argv/fkwargs do not add them
        if argname not in pkeys:
            continue
        # get value of argument
        value = p['INPUT'][argname]

        # value is either a list or a single value
        if type(value) not in [list, np.ndarray]:
            # generate this arguments log string
            log_string = '\t--{0}: {1}'.format(argname, str(value))
            log_strings.append(log_string)
        # else we have a list
        else:
            # get value
            indexvalues = get_arg_strval(value)
            # loop around index values
            for index, indexvalue in enumerate(indexvalues):
                # add to log strings
                largs = [argname, index, indexvalue]
                log_strings.append('\t--{0}[{1}]: {2}'.format(*largs))
    # -------------------------------------------------------------------------
    # log to screen and log file
    WLOG(p, 'info', ' Arguments used:')
    WLOG(p, 'info', log_strings, wrap=False)
    WLOG(p, '', HEADER)


# =============================================================================
# Indexing functions
# =============================================================================
def index_pp(p):
    # get index filename
    filename = spirouConfig.Constants.INDEX_OUTPUT_FILENAME()
    # get night name
    path = p['TMP_DIR']
    # get absolute path
    abspath = os.path.join(path, filename)
    # get the outputs
    outputs = p['OUTPUTS']
    # check that outputs is not empty
    if len(outputs) == 0:
        WLOG(p, '', 'No outputs to index, skipping indexing')
        return 0
    # get the index columns
    icolumns = spirouConfig.Constants.RAW_OUTPUT_COLUMNS(p)
    # ------------------------------------------------------------------------
    # index files
    istore = indexing(p, outputs, icolumns, abspath)
    # ------------------------------------------------------------------------
    # sort and save
    sort_and_save_outputs(p, istore, abspath)


def index_outputs(p):
    # get index filename
    filename = spirouConfig.Constants.INDEX_OUTPUT_FILENAME()
    # get night name
    path = p['REDUCED_DIR']
    # get absolute path
    abspath = os.path.join(path, filename)
    # get the outputs
    outputs = p['OUTPUTS']
    # check that outputs is not empty
    if len(outputs) == 0:
        WLOG(p, '', 'No outputs to index, skipping indexing')
        return 0
    # get the index columns
    icolumns = spirouConfig.Constants.REDUC_OUTPUT_COLUMNS(p)
    # ------------------------------------------------------------------------
    # index files
    istore = indexing(p, outputs, icolumns, abspath)
    # ------------------------------------------------------------------------
    # sort and save
    sort_and_save_outputs(p, istore, abspath)


def indexing(p, outputs, icolumns, abspath):
    # ------------------------------------------------------------------------
    # log indexing
    wmsg = 'Indexing outputs onto {0}'
    WLOG(p, '', wmsg.format(abspath))
    # construct a dictionary from outputs and icolumns
    istore = OrderedDict()
    # get output path
    opath = os.path.dirname(abspath)
    # looop around outputs
    for output in outputs:
        # get absfilename
        absoutput = os.path.join(opath, output)
        # get filename
        if 'FILENAME' not in istore:
            istore['FILENAME'] = [output]
            istore['LAST_MODIFIED'] = [os.path.getmtime(absoutput)]
        else:
            istore['FILENAME'].append(output)
            istore['LAST_MODIFIED'].append(os.path.getmtime(absoutput))

        # loop around index columns and add outputs to istore
        for icol in icolumns:
            # get value from outputs
            if icol not in outputs[output]:
                value = 'None'
            else:
                value = outputs[output][icol]
            # push in to istore
            if icol not in istore:
                istore[icol] = [value]
            else:
                istore[icol].append(value)
    # ------------------------------------------------------------------------
    # deal with file existing (add existing rows)
    if os.path.exists(abspath):
        # get the current index fits file
        idict = spirouImage.ReadFitsTable(p, abspath, return_dict=True)
        # check that all keys are in idict
        for key in icolumns:
            if key not in list(idict.keys()):
                wmsg1 = ('Warning: Index file does not have column="{0}"'
                         ''.format(key))
                wmsg2 = '\tPlease run the appropriate off_listing recipe'
                WLOG(p, 'warning', [wmsg1, wmsg2])
        # loop around rows in idict
        for row in range(len(idict['FILENAME'])):
            # skip if we already have this file
            if idict['FILENAME'][row] in istore['FILENAME']:
                continue
            # else add filename
            istore['FILENAME'].append(idict['FILENAME'][row])
            istore['LAST_MODIFIED'].append(idict['LAST_MODIFIED'][row])
            # loop around columns
            for icol in icolumns:
                # if column not in index deal with it
                if icol not in idict.keys():
                    istore[icol].append('None')
                else:
                    # add to the istore
                    istore[icol].append(idict[icol][row])
    # ------------------------------------------------------------------------
    return istore


def sort_and_save_outputs(p, istore, abspath):
    # ------------------------------------------------------------------------
    # sort the istore by column name and add to table
    sortmask = np.argsort(istore['FILENAME'])
    # loop around columns and apply sort
    for icol in istore:
        istore[icol] = np.array(istore[icol])[sortmask]
    # ------------------------------------------------------------------------
    # Make fits table and write fits table
    itable = spirouImage.MakeFitsTable(istore)
    spirouImage.WriteFitsTable(p, itable, abspath)


# =============================================================================
# Exit functions
# =============================================================================
def find_interactive():
    """
    Find whether user is using an interactive session

    i.e. True if:
        ipython code.py
        ipython >> run code.py
        python -i code.py

    False if
        python code.py
        code.py

    Note cannot distinguish between ipython from shell (so assumed interactive)

    :return cond: bool, True if interactive
    """
    cond1 = sys.flags.interactive
    cond2 = hasattr(sys, 'ps1')
    cond3 = not sys.stderr.isatty()
    return cond1 or cond2 or cond3


# noinspection PyUnresolvedReferences
def find_ipython():
    """
    Find whether user is using ipython or python

    :return using_ipython: bool, True if using ipython, false otherwise
    """
    try:
        # noinspection PyStatementEffect
        __IPYTHON__  # Note python wont define this, ipython will
        return True
    except NameError:
        return False


# =============================================================================
# Worker functions
# =============================================================================
def assign_pid():
    return 'PID-{0:020d}'.format(int(time.time() * 1e7))


def find_recipe(name=None):

    if name is None:
        empty = spirouRecipe.DrsRecipe(name='Empty')
        return empty

    found_recipe = None
    for recipe in RECIPES:
        if recipe.name == name:
            found_recipe = recipe
        elif recipe.name + '.py' == name:
            found_recipe = recipe
        elif recipe.name.strip('.py') == name:
            found_recipe = recipe
    if found_recipe is None:
        raise ValueError('No recipe named {0}'.format(name))
    # return
    return found_recipe


def get_arg_strval(value):
    """
    Get the string value representation of "value" (specifically for a listof
    DrsFitsFiles)

    :param value: object, the value to be printed
    :return out: string, the string representation of "object"
    """
    drs_file_type = spirouFile.DrsFitsFile

    # if list is empty --> return
    if len(value) == 0:
        return value

    # if we don't have a list of lists --> 1D array --> return
    if len(value) == 1:
        return value

    if type(value[1]) not in [list, np.ndarray]:
        return value

    # if we have a list of list we may have a DrsFile return
    if type(value[1][0]) == drs_file_type:
        out = []
        for it in range(len(value[0])):
            filename = os.path.basename(value[0][it])
            kind = value[1][it].name
            out.append('[{0}] {1}'.format(kind, filename))
        return out


def get_recipe_keys(args, remove_prefix=None, add=None, allow_skips=True):
    """
    Obtain the recipe keys from reipce "args"

    :param args: Dictionary containing key, value pairs where keys are the
                 argument names and values are instances of DrsArgument
    :param remove_prefix: string or None, a prefix to remove from keys if None
                          removes nothing
    :param add: list of strings or None, if not None each string is added to
                output "keys" as additional extra keys to check
    :param allow_skips: bool, if True allows special args to skip, if False
                        does not skip any special args

    :return keys: list of strings, the defined recipe keys (may be stipped of
                  a prefix if remove_prefix is not None)
    """
    # get the special keys
    keys = []

    for argname in args:
        arg = args[argname]
        # deal with skips (skips should not be added to keys here - unless
        #   allow_skips is set to False)
        if allow_skips and arg.kind == 'special':
            if arg.skip:
                keys += arg.names
        else:
            keys += arg.names

    # add additional keys (manually)
    if add is not None:
        keys += add
    # deal with removing prefixes
    if remove_prefix is not None:
        # set up storage
        old_keys = list(keys)
        keys = []
        for key in old_keys:
            # remove prefix
            while key[0] == remove_prefix:
                key = key[1:]
            # append to skeys
            keys.append(key)
    # return keys
    return keys


def keys_present(recipe, fkwargs=None, remove_prefix=None):
    """
    Returns a list of keys present in argument parsing (i.e. from sys.argv/or
    "fkwargs" - that is from call to function)

    :param recipe: DrsRecipe instance
    :param fkwargs: dictionary or None, the call dictionary to search (as well
                    as sys.argv)
    :param remove_prefix: string or None, a prefix to remove from keys if None
                          removes nothing
    :return keys: list of strings, the present keys (may be stipped of a prefix
                  if remove_prefix is not None)
    """
    # deal with no fkwargs
    if fkwargs is None:
        fkwargs = dict()
    # get they keys to check for
    arg_keys = get_recipe_keys(recipe.args)
    kwarg_keys = get_recipe_keys(recipe.kwargs, remove_prefix='-')
    skeys = get_recipe_keys(recipe.specialargs, add=['--help', '-h'],
                            allow_skips=False, remove_prefix='-')

    # need all positional keys
    keys = arg_keys
    # search for optional/special keys
    search_keys = kwarg_keys + skeys
    if len(search_keys) > 0:
        for search_key in search_keys:
            if search_for_key(search_key, fkwargs):
                keys.append(search_key)
    # deal with removing prefixes
    if remove_prefix is not None:
        # set up storage
        old_keys = list(keys)
        keys = []
        for key in old_keys:
            # remove prefix
            while key[0] == remove_prefix:
                key = key[1:]
            # append to skeys
            keys.append(key)
    # return found keys
    return keys


def search_for_key(key, fkwargs=None):
    """
    Search for a key in sys.argv (list of strings) and fkwargs (dictionary)
    in order to quickly tell if key was present when parsing arguments

    :param key: string, the key to look for
    :param fkwargs: dictionary or None, contains keywords from call

    :return cond: bool, True if key found in fkwargs/sys.argv, False otherwise
    """
    # deal with no fkwargs
    if fkwargs is None:
        fkwargs = dict()
    # search in fkwargs
    cond1 = key in fkwargs.keys()
    # search in sys.argv list of strings
    cond2 = False
    for argv in sys.argv:
        if key in argv:
            cond2 = True
    # return True if found and False otherwise
    if cond1 | cond2:
        return True
    else:
        return False


def set_debug_from_input(recipe, fkwargs):

    # assume debug is not there
    debug_arg = False
    # check sys.argv
    for arg in sys.argv:
        if '--debug' in arg:
            debug_arg = True
    # check fkwargs
    for kwarg in fkwargs:
        if '--debug' in kwarg:
            debug_arg = True

    # set DRS_DEBUG
    if debug_arg:
        # set the drs debug level to 1
        recipe.drs_params['DRS_DEBUG'] = 1
        # update the constants file
        spirouConfig.Constants.UPDATE_PP(recipe.drs_params)
    # return recipe
    return recipe


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

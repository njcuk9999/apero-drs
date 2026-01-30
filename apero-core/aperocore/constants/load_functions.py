#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-09-06 at 16:30

@author: cook
"""
import argparse
import os
import shutil
import time
from typing import Any, Dict, List, Union
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from aperocore import drs_lang
from aperocore.base import base
from aperocore.constants import constant_functions
from aperocore.constants.param_functions import ParamDict
from aperocore.constants.param_functions import SubParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from aperocore.core import drs_text

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.constants.load_functions'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get the Drs Exceptions
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# Get the text types
textentry = drs_lang.textentry
# get display func
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog
# Demo filter fields - customize to add/remove filter criteria
INFO_DICT_FILTERS = ['object', 'keywords']
# -----------------------------------------------------------------------------
# loaded cached versions
CONFIG_CACHE = dict()
PCONFIG_CACHE = dict()

ConstDict = constant_functions.ConstantsDict
Const = constant_functions.Const
Keyword = constant_functions.Keyword
KeywordDict = constant_functions.KeywordDict


# =============================================================================
# Define functions
# =============================================================================
def load_into_params(values: Dict[str, Any], sources: Dict[str, str],
                     instances: Dict[str, Const],
                     params: ParamDict = None,
                     check: bool = True) -> ParamDict:
    """
    Load a set of values/sources/instances into a parameter dictionary
    (recursively if there are dictionary/ParamDict instances)

    :param values: dict, the values to load
    :param sources: dict, the sources of the values
    :param instances: dict, the instances of the values
    :param params: ParamDict, the parameter dictionary to load into
    :param check: bool, if True check the values before adding them,
                  not this should only be set to False if checking elsewhere
                  is guaranteed

    :return: ParamDict containing the loaded constants
    """
    # set up a new parameter dictionary
    if params is None:
        params = ParamDict()
    # deal with instances being None
    if instances is None:
        return params
    # ignore list (used already)
    ignore_list = []
    # loop around keys
    for key in instances:
        # ignore keys already dealt with
        if key in ignore_list:
            continue
        # deal with no key in value
        if key not in values:
            values[key] = None
        # deal with no key in sources
        if key not in sources:
            sources[key] = 'Unknown'
        # if we have a dictionary or a ParamDict instance recursively load
        #  into a sub-PAramDict
        if isinstance(values[key], (dict, ParamDict)):
            # we only load a sub-dictionary if we don't have an associated
            # Const as an instance (Const can be dictionaries of values but
            # not dictionaries of Const)
            if not isinstance(instances[key], Const):
                # deal with already having values set (i.e. not None)
                if key in params:
                    _params = params[key]
                else:
                    _params = None
                # load nested dictionary
                params[key] = load_into_params(values[key], sources[key],
                                               instances[key], params=_params,
                                               check=check)
                # make sure parent instances/sources has the dictionaries of
                #   child instances/sources (otherwise we get in a mess)
                if isinstance(params[key], ParamDict):
                    params.instances[key] = params[key].instances
                    params.sources[key] = params[key].sources

                continue
        # ---------------------------------------------------------------------
        # special case - we have a dictionary (that has been flattened in
        # values)
        if values[key] is None and key in instances:
            # only do this if the instance dtype is a dictionary
            if hasattr(instances[key], 'dtype'):
                if instances[key].dtype is dict:
                    # start a new sub-dictionary
                    dict_values = dict()
                    # loop around all values
                    for dkey in values:
                        # if the key starts with key + '.' it is part of this
                        # dictionary
                        if dkey.startswith(key + '.'):
                            subkey = dkey[len(key) + 1:]
                            dict_values[subkey] = values[dkey]
                            # append to ignore list
                            ignore_list.append(dkey)
                    # if we have values change the value of this key from None
                    # to the dictionary we populated
                    if len(dict_values) > 0:
                        values[key] = dict_values
        # ---------------------------------------------------------------------
        # if we don't have an instance this is a new constants - which shouldn't
        #   really be allowed - we'll display a warning and hope the
        #   developer adds the constant to instances
        if key not in instances:
            # otherwise warn we are adding a foreign key/value to params
            wmsg = ('Key "{0}" not found in instances. To remove this warning'
                    ' make sure "{0}" is removes from input or added to the '
                    ' constants definitions for this module.')
            wargs = [key]
            AperoCodedWarning(None, None, targs=wargs, message=wmsg)
            # Push into params
            params.set(key, values[key], instance=None,
                       source=sources[key])
        # if the value is None and not currently in params set the value
        #   to None
        elif values[key] is None and key not in params:
            # set the value
            params.set(key, None, source=sources[key], instance=instances[key])
        # if the value is None and is already set do nothing
        elif values[key] is None:
            continue
        # if we are not checking just push value into parameters as is
        elif not check:
            params.set(key, values[key], source=sources[key],
                       instance=instances[key])
        # otherwise we verify the value before adding it
        else:
            # verify the value
            value = instances[key].validate(values[key], source=sources[key])
            # do not update key if value if None and it is already set
            if value is None and key in params:
                continue
            # set the value
            params.set(key, value, source=sources[key], instance=instances[key])
    # return the parameter dictionary
    return params


def load_parameters(config_list: List[Union[ConstDict, KeywordDict]] = None,
                    check: bool = True) -> ParamDict:
    """
    Load a set of Constants Dictionaries into a single Parameter Dictionary

    :param config_list: list of Constants Dictionaries
    :param check: bool, if True check the values before adding them,
                  not this should only be set to False if checking elsewhere
                  is guaranteed

    :return: tuple, 1. ParamDict containing the constants, 2. list of instances
                    (Const/Keyword instances) for each key
    """
    # ---------------------------------------------------------------------
    # store keys, values, sources, instances
    values, sources, instances = dict(), dict(), dict()
    # loop around config/constants/keyword dictionaries and merge
    for clist in config_list:
        # update value, source, instance based on
        values, sources, instances = clist.unpack(values, sources, instances)
    # ---------------------------------------------------------------------
    # push into a parameter dictionary
    params = load_into_params(values, sources, instances, check=check)
    # return these
    return params


def load_config(instruments: Dict[str, Any],
                instrument: Union[str, None] = None,
                from_file: bool = True, check: bool = True,
                cache: bool = True) -> ParamDict:
    """
    Load an instruments configuration into a Parameter Dictionary (ParamDict)

    :param instrument: str, the instrumnet config to load (can be None)
    :param from_file: bool, if True loads from user files (else loads from
                      module only
    :param cache: bool, use the cached parameters - no need to reload from
                  module - if True and cache present supersedes from_file
    :return: ParamDict containing the constants
    """
    global CONFIG_CACHE
    # set function name
    func_name = display_func('load_config', __NAME__)
    # deal with no instrument
    if instrument is None:
        instrument = base.IPARAMS['OBS.INSTRUMENT']
    elif instrument == 'default':
        instrument = 'None'
    # force instrument to upper case
    instrument = instrument.upper()
    # check config cache
    if instrument in CONFIG_CACHE and cache:
        return CONFIG_CACHE[instrument].copy()
    # otherwise get instrument class
    instrument_instance = load_pconfig(instruments, instrument)
    # get constants from modules
    clist = instrument_instance.get_clists()
    # push into params
    param_check = check and (not from_file)
    params = load_parameters(clist, check=param_check)
    # get constants from user config files
    if from_file:
        # get instrument user config files
        files = _get_file_names(params, instrument)
        # load keys, values, sources and instances from yaml files
        params = load_from_yaml(files, params)
    # finally push instrument into params
    params.set('INST', instrument_instance, source=func_name)
    # save sources to params
    params = _save_config_params(params)
    # cache these params
    if cache and from_file:
        CONFIG_CACHE[instrument] = params.copy()
    # -------------------------------------------------------------------------
    # if we don't have inputs add it (just as its added elsewhere)
    if 'INPUTS' not in params:
        params.set('INPUTS', ParamDict(), source=func_name)
    # -------------------------------------------------------------------------
    # return the parameter dictionary
    return params


def load_pconfig(instruments: Dict[str, Any],
                 instrument: Union[str, None] = None) -> Any:
    """
    Load an instrument pseudo constants

    :param instrument: str, the instrument to load pseudo constants for

    :return: the PesudoConstant class
    """
    # deal with no instrument
    if instrument is None:
        if len(base.IPARAMS) == 0:
            instrument = 'None'
        else:
            instrument = base.IPARAMS['OBS.INSTRUMENT']
    elif instrument == 'default':
        instrument = 'None'
    # force instrument to upper case
    instrument = instrument.upper()
    # if we already have the instrument cached
    if instrument in PCONFIG_CACHE:
        return PCONFIG_CACHE[instrument]
    # if we have the instrument
    if instrument in instruments:
        # start the instance and save it
        instrument_instance = instruments[instrument](instrument)
        # push into cache
        PCONFIG_CACHE[instrument] = instrument_instance
        # return this instance
        return instrument_instance
    # otherwise raise an exception
    emsg = 'Instrument "{0}" not found.'
    eargs = [instrument]
    raise AperoCodedException(None, '00-000-00000', targs=eargs,
                              message=emsg.format(*eargs))


def load_from_yaml(files: List[str], params: ParamDict = None) -> ParamDict:
    """
    Load constants/keywords from a yaml file

    :param files: list of strings, the file paths to the config/const files
    :param instances: list of Consts, the module paths

    :return: list of keys (str), list of values (Any), list of sources (str),
             list of instances (either Const or Keyword instances)
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('load_from_yaml', __NAME__)
    # deal with no parameters
    if params is None:
        params = ParamDict()
    # -------------------------------------------------------------------------
    # load constants from yaml file
    # -------------------------------------------------------------------------
    # loop around files
    for filename in files:
        # load the yaml in the standard way
        yaml_dict = base.load_yaml(filename)
        # flatten the dictionary
        flat_dict = _to_flat_dict(yaml_dict)
        # load all parameter instances into params
        instances = params.instances
        # for sources we copy the structure of yaml_dict
        sources = params.sources
        # load into params (make sure we definitely check the values)
        params = load_into_params(flat_dict, sources, instances, params,
                                  check=True)
    # return updated parameters
    return params


def load_from_cmd_args(params: ParamDict, cmd_kwargs: Dict[str, Any],
                       func_kwargs: Dict[str, Any] = None) -> ParamDict:
    """
    Push command line arguments into the parameter dictionary

    :param params: ParamDict, the parameter dictionary to load into
    :param cmd_kwargs: dict, the command line arguments
    :param func_kwargs: dict, the function keyword arguments
    :param source: str, the source of the command line arguments

    :return: ParamDict containing the loaded constants
    """
    # set up a new parameter dictionary
    if params is None:
        params = ParamDict()
    # deal with no func_kwargs
    if func_kwargs is None:
        func_kwargs = dict()
    # deal with instances being None
    if params.instances is None:
        return params
    # loop around keys
    for key in params.instances:
        # set up source
        # if we have a dictionary or a ParamDict instance recursively load
        #  into a sub-PAramDict
        if isinstance(params[key], ParamDict):
            params[key] = load_from_cmd_args(params[key], cmd_kwargs,
                                             func_kwargs)
            # make sure parent instances/sources has the dictionaries of
            #   child instances/sources (otherwise we get in a mess)
            if isinstance(params[key], ParamDict):
                params.sources[key] = params[key].sources
        # skip if we don't have an instance
        elif params.instances[key] is None:
            continue
        # else we try to get key from args
        else:
            # get the instance from params
            pinstance = params.instances[key]
            # get key from instances
            cmdkey = pinstance.cmd_arg
            # deal with no key
            if cmdkey is None:
                continue
            # -----------------------------------------------------------------
            # deal with getting the value (from function arguments or command)
            if (cmdkey not in func_kwargs) and (cmdkey not in cmd_kwargs):
                continue
            elif (cmdkey in func_kwargs) and (func_kwargs[cmdkey] is not None):
                value = func_kwargs[cmdkey]
                # deal with source
                source = 'function arguments'
            elif (cmdkey in cmd_kwargs) and (cmd_kwargs[cmdkey] is not None):
                value = cmd_kwargs[cmdkey]
                # deal with source
                source = 'command line arguments'
            else:
                continue
            # -----------------------------------------------------------------
            # deal with None (to not update)
            if value is None:
                continue
            # -----------------------------------------------------------------
            # verify the value
            value = params.instances[key].validate(value, source=source)
            # set the value
            params.set(key, value, source=source, instance=pinstance)
    # return the parameter dictionary
    return params


def get_all_params(name: str, description: str, inputargs: List[str],
                   config_list: List[Union[ConstDict, KeywordDict]] = None,
                   from_file: bool = True,
                   param_file_path: str = None,
                   external_const: Dict[str, Any] = None,
                   kwargs: Dict[str, Any] = None,
                   cmd_kwargs: Dict[str, Any] = None) -> ParamDict:
    """
    Get the parameters (default, command line and function call)

    :param name: str, the name of the recipe
    :param descriptions: dict, the descriptions of the recipes
    :param inputargs: dict, the allowed input arguments of the recipes
    :param config_list: list of Constants Dictionaries
    :param from_file: bool, if True loads from user files (else loads from
                        module only
    :param kwargs: any additional keywords to be passed to the recipe
    :param cmd_kwargs: Dict[str, Any] - override command line (does not call
                       command line - required for note books) must have all
                       keys contained in "inputargs"

    :return: ParamDict containing the constants
    """
    # get function name
    func_name = display_func('get_all_params', __NAME__)
    # add the external constants to the config list
    if external_const is not None:
        config_list = add_ext_config_list(config_list, external_const)
    # get the default arguments
    params = load_parameters(config_list)
    # set name
    if name is not None:
        params.set('RECIPE_SHORT', value=name.split('.')[-1],
                   source=func_name)
    # deal with overriding the command line arguments (i.e. in notebooks)
    if cmd_kwargs is not None and len(cmd_kwargs) > 0:
        args = dict(cmd_kwargs)
    # otherwise get the command line arguments
    else:
        args = cmd_args_from_clist(description, config_list, inputargs)
    # push in from command line arguments
    params = load_from_cmd_args(params, args, kwargs)
    # get constants from user config files
    if from_file:
        # get param file path
        param_file = get_param_file(params, param_file_path, func_name)
        # get instrument user config files
        largs = [[os.path.realpath(param_file)], params]
        # load keys, values, sources and instances from yaml files
        params = load_from_yaml(*largs)
    # make sure we have the minimal log parameters from wlog
    params = WLOG.minimal_params(params)
    # save the config list for use later
    params.set('CONFIG_LIST', config_list, source=func_name)
    # return params
    return params


def get_param_file(params: ParamDict, param_file_path: str,
                   func_name: str) -> str:
    # deal with no param file path
    if param_file_path is None:
        emsg = 'For {0} from_file is True must provide param_file_path'
        eargs = [func_name]
        WLOG(params, 'error', emsg.format(*eargs))
    # get the parameter file
    param_file = params[param_file_path]
    # deal with no param file
    if param_file is None:
        # ask user for yaml file name
        question = '\nPlease enter param file (.yaml) to load'
        # loop and ask
        param_file = drs_text.user_input(question, dtype='path',
                                         required=True)
    # check that param file exists
    if not os.path.exists(param_file):
        emsg = 'File "{0}" does not exist'
        eargs = [param_file]
        WLOG(params, 'error', emsg.format(*eargs))
    # update params with this param file
    params.set(param_file_path, os.path.realpath(param_file), source=func_name)
    # return path to file
    return params[param_file_path]


def cmd_args_from_clist(description: str = None,
                        config_list: List[Union[ConstDict, KeywordDict]] = None,
                        include_keys: List[str] = None,
                        ) -> Dict[str, Any]:
    """
    Get command line arguments from the constants dictionary

    :return:
    """
    # start parser
    parser = argparse.ArgumentParser(description=description)
    # storage of flattened list
    kwarg_list = dict()
    # loop around config/constants/keyword dictionaries and merge
    for clist in config_list:
        # get the flattened list of arguments
        kwarg_list = clist.cmd_args_from_clist(kwarg_list)
    # loop around all keys stored in dictionary
    for argname in kwarg_list:
        # deal with include list
        if include_keys is not None:
            if argname not in include_keys:
                continue
        # get the name keyword
        name = kwarg_list[argname]['name']
        # remove from kwargs
        kwarg_list[argname].pop('name')
        # add arguments
        parser.add_argument(name ,**kwarg_list[argname])
    # parse arguments
    args = parser.parse_args()
    # return arguments
    return vars(args)


def ask_for_missing_args(params: ParamDict,
                         include_keys: List[str] = None,
                         parent: str = None) -> ParamDict:
    """
    Ask the user for any missing arguments (recursively)
    based on a constant having the "not_none" flag set to True

    :param params: ParamDict, the parameter dictionary

    :return: ParamDict, the updated parameter dictionary
    """
    # set function name
    func_name = __NAME__ + '.ask_user_for_missing_arguments()'
    # set up parameters that are required and currently None in parameters
    for key in params:
        # ---------------------------------------------------------------------
        # deal with a parent
        if parent is None:
            outkey = key
        else:
            outkey = parent + '.' + key
        # ---------------------------------------------------------------------
        # deal with include list
        if include_keys is not None:
            if outkey not in include_keys:
                continue
        # ---------------------------------------------------------------------
        # deal with nested parameter dictionaries
        if isinstance(params[key], ParamDict):
            params[key] = ask_for_missing_args(params[key], include_keys,
                                               parent=outkey)
        # skip if value is not None
        if params[key] is not None:
            continue
        # get the parameter constant instance
        instance = params.instances[key]
        description = params.instances[key].description

        # see if we have to ask the user for this value
        if instance.not_none:
            # loop until we get a valid response from the user
            while True:
                question = ('\nPlease enter the value for {0}'
                            '\n\n{1}').format(key, description)
                # -------------------------------------------------------------
                # deal with dtype
                if instance.dtype in ['bool', bool]:
                    udtype = 'YN'
                elif instance.dtype in ['int', int, 'float', float, str, 'str']:
                    udtype = instance.dtype
                else:
                    udtype = str
                # -------------------------------------------------------------
                # loop and ask
                value = drs_text.user_input(question, dtype=udtype,
                                            options=instance.options,
                                            required=True)
                # validate value
                try:
                    value = instance.validate(test_value=value)
                except Exception as e:
                    print('Error: {0}'.format(e))
                    continue
                # if we get here the value is good
                break
            # set the value and source
            params.set(key, value, source=func_name)
    # return parameters
    return params


def add_ext_config_list(config_list: List[Union[ConstDict, KeywordDict]],
                        external_const: Dict[str, Union[ConstDict, KeywordDict]]
                        ) -> List[Union[ConstDict, KeywordDict]]:

    # deal with no config list
    if config_list is None:
        config_list = []
    # loop around external constants
    for key in external_const:
        # get the external constant
        econst = external_const[key]
        # deal with external constants not being a ConstDict
        if not isinstance(econst, ConstDict):
            emsg = 'External constants entry "{0}" must be ConstDict instances'
            eargs = [key]
            raise AperoCodedException(None, None, message=emsg.format(*eargs))
        # add to config list
        config_list.append(econst.get_nested(key))
    # return the updated config list
    return config_list


# =============================================================================
# Define starting point functions
# =============================================================================
def starting_point(params: ParamDict, imode_key: Union[str, List[str]],
                   demo_dict: Dict[str, Dict[str, Any]]) -> ParamDict:
    """
    Modify the parameters by a specific starting point (i.e. a demo)

    :param params: ParamDict, parameter dictionary of constants
    :param imode_key: str, the key of the instrument mode (in params)
    :param demo_module: the module for demos (needs dict DEMOS)

    :return: ParamDict, the updated parameter dictionary of constants
    """
    # set function name
    func_name = display_func('starting_point', __NAME__)
    # deal with instrument mode not set
    params = ask_for_missing_args(params, include_keys=[imode_key])
    # section start
    msg = ('\nPlease choose a demo mode to start from. '
           '\n\nNote this can be used as a starting point for any other '
           'observation. '
           '\n\nEven if you do not '
           'want to run the demo we suggest taking a look at the demo yaml, '
           'copying the yaml configuration file and modifiying it yourself '
           'instead of starting from default values or a a blank yaml.')
    drs_text.cprint(msg, 'g')
    # get user selected instrument mode
    imode = params[imode_key]
    # create storage for the demo download data
    demo_params = dict(ACTIVE=False, URL=None, DOWNLOAD=dict(), ID=None)
    # deal with no demos for this mode
    if imode not in demo_dict:
        # print that no demos are avaiable
        wmsg = (f'No demos available for {imode} '
                f'-- starting from default values. \n\n'
                f'Warning we highly do not recommend this '
                f'without assistance from the developers.')
        WLOG(params, 'warning', wmsg)
        # set demo params
        params.set('DEMO_PARAMS', demo_params, source=func_name)
        # ask for all remaining missing parameters
        params = ask_for_missing_args(params)
        # return parameters
        return params
    # get the demos for this instrument
    idemos = demo_dict[imode]
    # allow filtering by object and keywords
    idemos = _filter_demo_choices(params, idemos)
    # display the possible starting points for this instrument mode
    counters = dict()
    # loop through demos
    for it, demo_mode in enumerate(idemos):
        # get the demo class
        demo_inst = idemos[demo_mode]
        # get the info dictionary
        info_dict = demo_inst.INFO
        # push the name of the demo for debugging purposes
        info_dict['__NAME__'] = demo_inst.__NAME__
        # display info for mode
        _print_info(params, it + 1, info_dict)
        # add to counter
        counters[str(it + 1)] = demo_mode

    # ask user to select mode
    while True:
        userinput = str(input('\nEnter a number to start from a demo '
                              'or press enter (to not use a demo):\t'))
        # New line for clarity
        print()
        # clean user input
        userinput = userinput.lower().strip()
        # deal with user options
        if userinput in ['', 'none', '0', 'null']:
            break
        elif userinput in counters.keys():
            # push demo parameters into params
            params = _load_info(params, idemos[counters[userinput]])
            # update the demo_params
            demo_params['ACTIVE'] = True
            demo_params['URL'] = idemos[counters[userinput]].URL
            demo_params['DOWNLOAD'] = idemos[counters[userinput]].DOWNLOAD
            demo_params['ID'] = idemos[counters[userinput]].INFO['id']
            # break out of the while loop here
            break
        else:
            msg = f'Invalid input: {0}'
            margs = [userinput]
            WLOG(params, 'warning', msg.format(*margs))

    # set demo params
    params.set('DEMO_PARAMS', demo_params, source=func_name)
    # return parameters
    return params


def _print_info(params: ParamDict, it: int, info_dict: Dict[str, str]):
    """
    Print info about a demo mode

    :param params: ParamDict, the parameter dictionary of constants
    :param it: int, index of the demo mode (for user selectiong)
    :param info_dict: Dict[str, str], the info about a demo mode

    :return: str, the info about a demo mode
    """
    # add header bar
    drs_text.cprint('\n' + '*' * 70, 'b')
    # deal with no title in info (required)
    if 'title' not in info_dict:
        emsg = 'Demo {0} INFO does not have a title'
        eargs = [info_dict['__NAME__']]
        raise AperoCodedException(params, None, message=emsg.format(*eargs))
    # add title text
    drs_text.cprint('* {0}: {1}'.format(it, info_dict['title']), 'b')
    # add header bar
    drs_text.cprint('*' * 70, 'b')
    # add rest of the info
    for info_key in info_dict:
        # already dealt with title
        if info_key in ['title', '__NAME__']:
            continue
        # deal with printing values
        if isinstance(info_dict[info_key], list):
            str_value = ''
            for ii in info_dict[info_key]:
                str_value += '\n\t\t - ' + str(ii)
        else:
            str_value = str(info_dict[info_key])
        # print other info
        msg = '\t{0}: {1}'
        margs = [info_key, str_value]
        print(msg.format(*margs))


def _parse_demo_filter(userinput: str) -> List[str]:
    """
    Parse user input into filter tokens.

    :param userinput: str, user input string

    :return: list of lowercase tokens
    """
    if userinput is None:
        return []
    raw = userinput.replace(',', ' ')
    tokens = [t.strip().lower() for t in raw.split() if t.strip()]
    return tokens


def _normalize_demo_field(value: Any) -> List[str]:
    """
    Normalize a demo field to a list of lowercase strings.

    :param value: Any, field value

    :return: list of strings
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        items = value
    else:
        items = [value]
    out = []
    for item in items:
        text = str(item).strip().lower()
        if text:
            out.append(text)
    return out


def _demo_matches_filter(info_dict: Dict[str, Any],
                         tokens: List[str]) -> bool:
    """
    Check whether a demo matches the filter tokens using
    INFO_DICT_FILTERS.

    :param info_dict: Dict[str, Any], demo INFO dict
    :param tokens: list of tokens to match

    :return: bool, True if demo matches
    """
    if not tokens:
        return True
    # build haystack from available filter fields
    haystack = []
    for field in INFO_DICT_FILTERS:
        if field in info_dict:
            terms = _normalize_demo_field(info_dict[field])
            haystack.extend(terms)
    # if no filter fields found, demo doesn't match
    if not haystack:
        return False
    # match all tokens
    for token in tokens:
        if not any(token in term for term in haystack):
            return False
    return True


def _collect_filter_values(idemos: Dict[str, Any]) -> Dict[str, set]:
    """
    Collect all available filter values from demos.

    :param idemos: dict of demos for the instrument mode

    :return: dict mapping filter field to set of available values
    """
    filter_values = {field: set() for field in INFO_DICT_FILTERS}
    for demo_mode in idemos:
        demo_inst = idemos[demo_mode]
        info_dict = demo_inst.INFO
        for field in INFO_DICT_FILTERS:
            if field in info_dict:
                terms = _normalize_demo_field(info_dict[field])
                filter_values[field].update(terms)
    return filter_values


def _should_skip_filtering(filter_values: Dict[str, set]) -> bool:
    """
    Determine if filtering should be skipped (only one choice).

    Skip if:
    - All fields have exactly one value, OR
    - Only one unique value exists across all fields

    :param filter_values: dict mapping filter field to set of values

    :return: bool, True if filtering should be skipped
    """
    # count total unique values across all fields
    all_values = set()
    for field in INFO_DICT_FILTERS:
        if field in filter_values:
            all_values.update(filter_values[field])
    # if only one total unique value, skip
    if len(all_values) <= 1:
        return True
    # if all fields have exactly one value, skip
    for field in INFO_DICT_FILTERS:
        if field in filter_values:
            if len(filter_values[field]) != 1:
                return False
    return True


def _build_filter_prompt(filter_values: Dict[str, set]) -> str:
    """
    Build the filter prompt showing available values.
    Only shows fields with multiple values.

    :param filter_values: dict mapping filter field to set of values

    :return: formatted prompt string
    """
    lines = ['\nFilter demos by:']
    shown_count = 0
    for field in INFO_DICT_FILTERS:
        if field in filter_values and len(filter_values[field]) > 1:
            values = ', '.join(sorted(filter_values[field]))
            lines.append(f'  {field}: {values}')
            shown_count += 1
    lines.append('(enter to skip): ')
    return '\n'.join(lines)


def _filter_demo_choices(params: ParamDict,
                         idemos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter demos by object/keywords without assuming fields exist.

    :param params: ParamDict, parameter dictionary of constants
    :param idemos: dict of demos for the instrument mode

    :return: filtered demo dict
    """
    if not isinstance(idemos, dict) or len(idemos) == 0:
        return idemos
    # collect available filter values
    filter_values = _collect_filter_values(idemos)
    # skip filtering if only one choice
    if _should_skip_filtering(filter_values):
        return idemos
    # build prompt with available values
    prompt = _build_filter_prompt(filter_values)
    while True:
        userinput = str(input(prompt)).strip()
        if userinput == '':
            return idemos
        tokens = _parse_demo_filter(userinput)
        if not tokens:
            return idemos
        filtered = dict()
        for demo_mode in idemos:
            demo_inst = idemos[demo_mode]
            info_dict = demo_inst.INFO
            if _demo_matches_filter(info_dict, tokens):
                filtered[demo_mode] = demo_inst
        if len(filtered) > 0:
            return filtered
        msg = ('No demos match that filter. Try again or press enter '
               'to skip.')
        WLOG(params, 'warning', msg)


def _load_info(params: ParamDict, demo_inst) -> ParamDict:
    """
    Load the info from a demo

    :param params: ParamDict
    :param demo_inst: module - the demo python code selected

    :return: The updated parameter dictionary
    """
    # get the cdict
    cdict = demo_inst.Cdict
    # get the title
    title = demo_inst.INFO['title']
    # print overriding
    msg = 'Starting from DEMO: "{0}"'
    margs = [title]
    WLOG(params, 'info', msg.format(*margs))
    # log that we are overriding the following values
    msg = 'Overriding the following values:'
    WLOG(params, '', msg)
    # add a pause here
    time.sleep(0.1)
    # loop around keys in storage
    for key in cdict.storage:
        # only deal with keys already defined in parameters
        if key in params:
            # don't override values from the command line
            if 'command' in params.sources[key]:
                continue
            # get new value
            new_value = cdict.storage[key].value
            # get old value
            old_value = params[key]
            # do not update values that are None
            if new_value is None:
                continue
            # only update keys that have changed
            if new_value != old_value:
                # print the value we are starting with
                _print_parameters(key, new_value)
                # set the value
                params.set(key, new_value, source=demo_inst.__NAME__,
                           instance=params.instances[key])
    # return parameters
    return params


def _validate_url(url: str, params: ParamDict = None) -> bool:
    """
    Validate that a URL is accessible by attempting to open it

    :param url: str, the URL to validate
    :param params: ParamDict, the parameter dictionary for logging

    :return: bool, True if URL is valid and accessible, False otherwise
    """
    try:
        # attempt to open the URL with a timeout
        response = urlopen(url, timeout=5)
        response.close()
        return True
    except (HTTPError, URLError) as e:
        # log warning if params provided
        if params is not None:
            msg = f'URL validation failed: {url}\nError: {str(e)}'
            WLOG(params, 'warning', msg)
        return False
    except Exception as e:
        # handle other exceptions
        if params is not None:
            msg = f'URL validation error: {url}\nError: {str(e)}'
            WLOG(params, 'warning', msg)
        return False

def ask_about_download_data(params, url):
    # set initial values
    demolocal = None
    demosymlink = False
    # loop until we get valid input
    while True:
        # ask user what they want to do
        prompt = ('\nHow would you like to handle demo data?\n'
                  f'  [D]ownload from our URL ({url})\n'
                  f'  [U]se a custom URL\n'
                  f'  [L]ocal link (on disk)\n'
                  f'  [S]kip downloading data\n')
        userinput = str(input(prompt)).upper().strip()
        # handle skip option
        if userinput in ['S', 'SKIP']:
            return
        if userinput in ['U', 'USE']:
            # ask user for custom url
            while True:
                prompt_url = ('\nProvide the URL to demo data '
                              '(or [Q]uit): ')
                user_url = str(input(prompt_url)).strip()
                # handle quit option
                if user_url.upper() in ['Q', 'QUIT']:
                    return
                # validate url format and accessibility
                if (user_url.startswith('http://') or
                        user_url.startswith('https://')):
                    # test if URL is accessible
                    if _validate_url(user_url, params):
                        url = user_url
                        msg = f'URL validated successfully: {url}'
                        WLOG(params, 'info', msg)
                        break
                    else:
                        msg = (
                            f'URL is not accessible: {user_url}. '
                            'Please try again.'
                        )
                        WLOG(params, 'warning', msg)
                else:
                    msg = (
                        f'Invalid URL format: {user_url}. '
                        'URL must start with http:// or https://. '
                        'Please try again.'
                    )
                    WLOG(params, 'warning', msg)
        # handle download option (from provided link)
        elif userinput in ['D', 'DOWNLOAD']:
            demolocal = None
            break
        # handle local link option
        elif userinput in ['L', 'LOCAL']:
            # ask user for local path
            while True:
                prompt_local = (
                    '\nProvide the local path to demo data '
                    '(or [Q]uit): '
                )
                user_path = (
                    str(input(prompt_local)).strip()
                )
                # handle quit option
                if user_path.upper() in ['Q', 'QUIT']:
                    return
                # validate path exists
                if os.path.isdir(user_path):
                    demolocal = user_path
                    # ask user about symlinks
                    symlink_prompt = (
                        '\nUse symlinks? '
                        '[Y]es (symlinks) or [N]o '
                        '(hard copy): '
                    )
                    symlink_input = (
                        str(input(symlink_prompt)).upper().strip()
                    )
                    if symlink_input in ['Y', 'YES']:
                        demosymlink = True
                    else:
                        demosymlink = False
                    break
                else:
                    msg = (
                        f'Path does not exist: {user_path}. '
                        'Please try again.'
                    )
                    WLOG(params, 'warning', msg)
            break
        else:
            msg = (
                'Invalid choice. Please select [D]ownload, '
                '[L]ocal, or [S]kip.'
            )
            WLOG(params, 'warning', msg)
    # return updated values
    return url, demolocal, demosymlink


def download_data(params: ParamDict, demolocal: str = None,
                  demosymlink: bool = False):
    """
    Download the data from a demo or copy from a local repository

    Note you must have DEMO_PARAMS in params for this function to work

    DEMO_PARAMS: dict, the demo parameters dictionary

    DEMO_PARAMS['ACTIVE']: bool: if True try to download data, else return
    DEMO_PARAMS['URL']: str: the url of the demo
    DEMO_PARAMS['DOWNLOAD']: Dict[str, str]
          - key = str: the parameters to look for files
          - value = str: the parameter description the path to save locally

    :param params: ParamDict, the parameter dictionary of constants
    :param demolocal: str or None, if not None path to local demo data
                      repository to copy/symlink from instead of downloading
    :param demosymlink: bool, if True and demolocal is not None, create
                        symlinks instead of copying files

    :return: None, downloads data from URL to local file(S), copies from
             local repository, or creates symlinks
    """
    # set function name
    func_name = display_func('download_data', __NAME__)
    # deal with params not set up properly
    if 'DEMO_PARAMS' not in params:
        # display error about using this function without DEMO_PARAMS
        # TODO: Add to language database
        emsg = 'params does not contain DEMO_PARAMS cannot use function {0}'
        eargs = [func_name]
        raise AperoCodedException(params, None, message=emsg.format(*eargs))
    # get the parameters from demo parameters
    active = params['DEMO_PARAMS']['ACTIVE']
    url = params['DEMO_PARAMS']['URL']
    download = params['DEMO_PARAMS']['DOWNLOAD']
    # -------------------------------------------------------------------------
    # deal with not being active
    if not active:
        return
    # -------------------------------------------------------------------------
    # ask the user how they want to handle demo data
    if demolocal is None:
        url, demolocal, demosymlink = ask_about_download_data(params, url)
    # -------------------------------------------------------------------------
    # print progress
    if demolocal is None:
        WLOG(params, 'info', f'Downloading data. Please wait...')
    elif demosymlink:
        msg = 'Creating symlinks to data from local repository...'
        WLOG(params, 'info', msg)
    else:
        WLOG(params, 'info', f'Copying data from local repository...')
    # -------------------------------------------------------------------------
    # loop around downloadable parameters
    for parameter in download:
        # get download parameter
        dparameter = download[parameter]
        # deal with parameter not in params
        if parameter not in params:
            WLOG(params, 'warning', f'Parameter "{parameter}" not defined')
            continue
        # deal with value of DOWNLOAD[parameter] not in params
        if dparameter not in params:
            msg = f'Parameter "{dparameter}" not defined'
            WLOG(params, 'warning', msg)
            continue
        # deal with parameter being None
        if params[parameter] is None:
            continue
        # deal with dparameter being None
        if params[dparameter] is None:
            continue
        # get the filename
        value = params[parameter]
        # force into a list (if string)
        if isinstance(value, str):
            value = [value]
        # deal with bad parameter (should now be a list)
        if not isinstance(value, list):
            msg = f'Cannot get parameter: "{parameter}"'
            WLOG(params, 'warning', msg)
            continue
        # create path if it doesn't exist
        if not os.path.exists(params[dparameter]):
            os.makedirs(params[dparameter])
        # loop around values and try to download or copy
        for value_it in value:
            # construct the local file name
            localpath = str(os.path.join(params[dparameter], value_it))
            # deal with files already existing -- don't re-download/copy
            if os.path.exists(localpath):
                continue
            # handle local copy vs remote download
            if demolocal is not None:
                # get the last directory component from the url
                url_parts = url.rstrip('/').split('/')
                last_dir = url_parts[-1]
                # construct source path from local repository
                src_path = str(os.path.join(demolocal, last_dir, value_it))
                # check if source exists
                if not os.path.exists(src_path):
                    msg = (f'Local data not found at: {src_path}')
                    WLOG(params, 'warning', msg)
                    continue
                # handle symlink vs copy
                if demosymlink:
                    # print progress
                    msg = '\tSymlinking: {0}'
                    margs = [localpath]
                    WLOG(params, '', msg.format(*margs))
                    # create symlink (works cross-platform)
                    os.symlink(src_path, localpath)
                else:
                    # print progress
                    msg = '\tCopying: {0}'
                    margs = [localpath]
                    WLOG(params, '', msg.format(*margs))
                    # copy the file
                    import shutil
                    shutil.copy2(src_path, localpath)
            else:
                # get the url
                purl = f'{url}/{value_it}'
                # print progress
                msg = '\tDownloading: {0}'
                margs = [localpath]
                WLOG(params, '', msg.format(*margs))
                # try to get the data
                drs_misc.download_file(purl, localpath)


def _print_parameters(key: str, value: Any):
    """
    Print a parameter similar to how it would appear in a yaml dict
    
    :param key: str, the name of the parameter in the ParamDict
    :param value: Any, the value of the parameter

    :return: None, prints to standard output
    """
    # ignore param dicts
    if isinstance(value, (ParamDict, SubParamDict, ConstDict)):
        return
    if isinstance(value, list):
        drs_text.cprint(f'|| {key}:', 'g')
        for val in value:
            drs_text.cprint(f'|| \t - {val}')
    elif isinstance(value, dict):
        drs_text.cprint(f'|| {key}:', 'g')
        for subkey in value:
            drs_text.cprint(f'|| \t {subkey}: {value[subkey]}', 'g')
    else:
        drs_text.cprint(f'|| {key}: {value}', 'g')



# =============================================================================
# Config loading private functions
# =============================================================================
def warninglogger(instruments: Dict[str, Any], warnlist: Any,
                  funcname: Union[str, None] = None):
    """
    Warning logger - takes "w" - a list of caught warnings and pipes them on
    to the log functions. If "funcname" is not None then t "funcname" is
    printed with the line reference (intended to be used to identify the code/
    function/module warning was generated in)

    to catch warnings use the following:

    >> import warnings
    >> with warnings.catch_warnings(record=True) as warnlist:
    >>     code_to_generate_warnings()
    >> warninglogger(parmas, warnlist, 'some function name for logging')

    :param instruments: dictionary of instruments
    :param warnlist: list of warnings, the list of warnings from
                     warnings.catch_warnings
    :param funcname: string or None, if string then also pipes "funcname" to the
                     warning message (intended to be used to identify the code/
                     function/module warning was generated in)
    :return:
    """
    # get pconstant
    params = load_config(instruments)
    log_warnings = params['LOG.CAUGHT_WARNINGS']
    # deal with warnlist as string
    if isinstance(warnlist, str):
        warnlist = [warnlist]
    # deal with warnings
    displayed_warnings = []
    if log_warnings and (len(warnlist) > 0):
        for warnitem in warnlist:
            # if we have a function name then use it else just report the
            #    line number (not recommended)
            if funcname is None:
                wargs = [warnitem.lineno, '', warnitem.message]
            else:
                wargs = [warnitem.lineno, '({0})'.format(funcname),
                         warnitem.message]
            # log message
            key = '10-005-00001'
            wmsg = textentry(key, args=wargs)
            # if we have already display this warning don't again
            if wmsg in displayed_warnings:
                continue
            else:
                AperoCodedWarning(params, '10-005-00001', targs=wargs,
                                  sublevel=5)
                displayed_warnings.append(wmsg)


def _save_config_params(params: ParamDict) -> ParamDict:
    """
    Adds 'DRS_CONFIG' list of config files to parameter dictionary

    :param params: ParamDict - the parameter dictionary of constants

    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('_save_config_params', __NAME__)
    # get sources from paramater dictionary
    sources = params.sources.values()
    # get unique sources
    usources = set(sources)
    # set up storage
    params['DRS_CONFIG'] = []
    params.set_source('DRS_CONFIG', func_name)
    # loop around and add to param
    for source in usources:
        if source is not None:
            params['DRS_CONFIG'].append(source)
    # return the parameters
    return params


def _get_file_names(params: ParamDict,
                    instrument: Union[str, None] = None) -> List[str]:
    """
    Lists the users config / constants files for the specific instrument
    if None are found returns the default files

    :param params: Paramdict - parameter dictionary
    :param instrument: str, the instrument to list files for
    :return: list of strings - the config /constant files found
    """
    # set function name (cannot break here --> no access to inputs)
    # func_name = display_func('_get_file_names', __NAME__)
    # deal with no instrument
    if drs_text.null_text(instrument, ['None', '']):
        return []
    # get user environmental path
    user_env = params['DRS.USERENV']
    # get the user scripts
    yscripts = params['DRS.USER_SCRIPTS']
    # deal with no user environment and no default path
    if user_env is None:
        return []
    # set empty directory
    config_dir = None
    # -------------------------------------------------------------------------
    # User environmental path
    # -------------------------------------------------------------------------
    # check environmental path exists
    if user_env in os.environ:
        # get value
        path = os.environ[user_env]
        # check that directory linked exists
        if os.path.exists(path):
            # set directory
            config_dir = path
    # -------------------------------------------------------------------------
    # if directory is still empty return empty list
    if config_dir is None:
        return []
    # -------------------------------------------------------------------------
    # look for user configurations within instrument sub-folder
    # -------------------------------------------------------------------------
    config_files = []
    for script in yscripts:
        # construct path
        config_path = os.path.join(config_dir, script)
        # check that it exists
        if os.path.exists(config_path):
            config_files.append(config_path)
    # deal with no files found
    if len(config_files) == 0:
        wargs = [config_dir, ','.join(yscripts)]
        AperoCodedWarning(None,'00-003-00036', targs=wargs)
    # return files
    return config_files


def _to_flat_dict(nested_dict, parent_key=''):
    flat_dict = {}
    for key, value in nested_dict.items():
        # get the full key
        full_key = f"{parent_key}.{key}" if parent_key else key
        # Check if the value is a dictionary
        if isinstance(value, dict):
            # Recurse into sub-dictionary
            flat_dict.update(_to_flat_dict(value, full_key))
        else:
            # Add the key-value pair to the flat dictionary
            flat_dict[full_key] = value
    # return the flattened dictionary
    return flat_dict


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

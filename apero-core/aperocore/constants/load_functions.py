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
from typing import Any, Dict, List, Optional, Tuple, Union

from aperocore.base import base
from aperocore.core import drs_base_classes as base_class
from aperocore.constants.param_functions import ParamDict
from aperocore.constants import constant_functions
from aperocore import drs_lang
from aperocore.core import drs_exceptions
from aperocore.core import drs_misc
from aperocore.core import drs_text
from aperocore.core import drs_log

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
    # loop around keys
    for key in instances:
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
                from_file: bool = True,
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
        instrument = base.IPARAMS['INSTRUMENT']
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
    params = load_parameters(clist, check=not from_file)
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
            instrument = base.IPARAMS['INSTRUMENT']
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
    # define dict types
    dict_types = (dict, ParamDict, ConstDict)
    # -------------------------------------------------------------------------
    # load constants from yaml file
    # -------------------------------------------------------------------------
    # loop around files
    for filename in files:
        # load the yaml in the standard way
        yaml_dict = base.load_yaml(filename)
        # load all parameter instances into params
        margs = [params, params, 'instances', dict_types]
        instances = drs_misc.map_nested_attribute_dict(*margs)
        # for sources we copy the structure of yaml_dict
        sources = drs_misc.create_structure_like(yaml_dict, func_name)
        # load into params (make sure we definitely check the values)
        params = load_into_params(yaml_dict, sources, instances, params,
                                  check=True)
    # return updated parameters
    return params


def load_from_cmd_args(params: ParamDict, cmd_kwargs: Dict[str, Any],
                       func_kwargs: Dict[str, Any]) -> ParamDict:
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
                   **kwargs) -> ParamDict:
    """
    Get the parameters (default, command line and function call)

    :param name: str, the name of the recipe
    :param descriptions: dict, the descriptions of the recipes
    :param inputargs: dict, the allowed input arguments of the recipes
    :param config_list: list of Constants Dictionaries
    :param from_file: bool, if True loads from user files (else loads from
                        module only
    :param kwargs: any additional keywords to be passed to the recipe

    :return: ParamDict containing the constants
    """
    # get function name
    func_name = display_func('get_all_params', __NAME__)
    # get the default arguments
    params = load_parameters(config_list)
    # set name
    if name is not None:
        params.set('RECIPE_SHORT', value=name.split('.')[-1],
                   source=func_name)
    # get the yaml file
    args = cmd_args_from_clist(description, config_list, inputargs)
    # push in from command line arguments
    params = load_from_cmd_args(params, args, kwargs)
    # get constants from user config files
    if from_file:
        if param_file_path is None:
            emsg = 'For {0} from_file is True must provide param_file_path'
            eargs = [func_name]
            WLOG(params, 'error', emsg.format(*eargs))
        # get the parameter file
        param_file = params[param_file_path]
        # get instrument user config files
        largs = [[os.path.realpath(param_file)], params]
        # load keys, values, sources and instances from yaml files
        params = load_from_yaml(*largs)
    # make sure we have the minimal log parameters from wlog
    params = WLOG.minimal_params(params)
    # return params
    return params


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

        # see if we have to ask the user for this value
        if instance.not_none:
            # loop until we get a valid response from the user
            while True:
                question = '\nPlease enter the value for {0}'.format(key)
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
    pconstant = load_pconfig(instruments)
    log_warnings = pconstant.LOG_CAUGHT_WARNINGS()
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
                AperoCodedWarning(None, '10-005-00001', targs=wargs,
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
    func_name = display_func('_get_file_names', __NAME__)
    # deal with no instrument
    if drs_text.null_text(instrument, ['None', '']):
        return []
    # get user environmental path
    user_env = params['DRS_USERENV']
    # get the user scripts
    yscripts = params['USER_SCRIPTS']
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

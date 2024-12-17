#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-09-06 at 16:30

@author: cook
"""
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
                     params: ParamDict = None) -> ParamDict:
    """
    Load a set of values/sources/instances into a parameter dictionary
    (recursively if there are dictionary/ParamDict instances)

    :param values: dict, the values to load
    """
    # set up a new parameter dictionary
    if params is None:
        params = ParamDict()
    # loop around keys
    for key in instances:
        # if we have a dictionary or a ParamDict instance recursively load
        #  into a sub-PAramDict
        if isinstance(values[key], (dict, ParamDict)):
            params[key] = load_into_params(values[key], sources[key],
                                           instances[key])
        # if we don't have an instance this is a new constants - which shouldn't
        #   really be allowed - we'll display a warning and hope the
        #   developer adds the constant to instances
        elif key not in instances:

            wmsg = ('Key "{0}" not found in instances. To remove this warning'
                    ' make sure "{0}" is removes from input or added to the '
                    ' constants definitions for this module.')
            wargs = [key]
            AperoCodedWarning(None, None, targs=wargs, message=wmsg)
            # Push into params
            params.set(key, values[key], instance=None,
                       source=sources[key])
        elif values[key] is None:
            # set the value
            params.set(key, None, source=sources[key], instance=instances[key])
        else:
            # verify the value
            value = instances[key].validate(values[key], source=sources[key])
            # set the value
            params.set(key, value, source=sources[key], instance=instances[key])
    # return the parameter dictionary
    return params


def load_parameters(config_list: List[Union[ConstDict, KeywordDict]] = None
                    ) -> ParamDict:
    """
    Load a set of Constants Dictionaries into a single Parameter Dictionary

    :param config_list: list of Constants Dictionaries

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
    params = load_into_params(values, sources, instances)
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
    params = load_parameters(clist)
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


# =============================================================================
# Config loading private functions
# =============================================================================
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
        # load all parameter instances into params
        instances = drs_misc.map_nested_attribute_dict(yaml_dict, params,
                                                       'instances')
        # for sources we copy the structure of yaml_dict
        sources = drs_misc.create_structure_like(yaml_dict, func_name)
        # load into params
        params = load_into_params(yaml_dict, sources, instances, params)
    # return updated parameters
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

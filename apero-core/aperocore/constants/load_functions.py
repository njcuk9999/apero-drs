#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-09-06 at 16:30

@author: cook
"""
import os
from typing import Any, Dict, List, Tuple, Union

from aperocore.base import base
from aperocore.core import drs_base_classes as base_class
from aperocore.constants.param_functions import ParamDict
from aperocore import drs_lang
from aperocore.core import drs_exceptions
from aperocore.core import drs_misc
from aperocore.core import drs_text
from apero.instruments import select

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
DrsCodedException = drs_exceptions.DrsCodedException
DrsCodedWarning = drs_exceptions.DrsCodedWarning
# Get the text types
textentry = drs_lang.textentry
# get display func
display_func = drs_misc.display_func
# -----------------------------------------------------------------------------
# loaded cached versions
CONFIG_CACHE = dict()
PCONFIG_CACHE = dict()


# =============================================================================
# Define functions
# =============================================================================
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
    # get constants from instrument
    instrument_instance.get_constants()
    # get constants from modules
    values, sources, instances = instrument_instance.get_constants()
    # push into a parameter dictionary
    params = ParamDict(values)
    # add to params
    for key in instances:
        # set source
        params.set_source(key, sources[key])
        # set instance (Const/Keyword instance)
        params.set_instance(key, instances[key])
    # get constants from user config files
    if from_file:
        # get instrument user config files
        files = _get_file_names(params, instrument)
        # load keys, values, sources and instances from yaml files
        ovalues, osources, oinstances = _load_from_yaml(files, instances)
        # add to params
        for key in ovalues:
            # set value
            params[key] = ovalues[key]
            # set instance (Const/Keyword instance)
            params.set_instance(key, oinstances[key])
            params.set_source(key, osources[key])
    # finally push instrument into params
    params['INST'] = instrument_instance
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
    raise DrsCodedException('00-000-00000', targs=eargs, level='error',
                            message=emsg.format(*eargs))


def warninglogger(params: Any, warnlist: Any,
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

    :param params: ParamDict, the constants dictionary passed in call
    :param warnlist: list of warnings, the list of warnings from
                     warnings.catch_warnings
    :param funcname: string or None, if string then also pipes "funcname" to the
                     warning message (intended to be used to identify the code/
                     function/module warning was generated in)
    :return:
    """
    # get pconstant
    pconstant = load_pconfig(select.INSTRUMENTS)
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
                drs_exceptions.DrsCodedWarning(key, 'warnning', message=wmsg)
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
        DrsCodedWarning('00-003-00036', 'warning', targs=wargs,
                        func_name=func_name)
    # return files
    return config_files


def _load_from_yaml(files: List[str], instances: Dict[str, Any]
                    ) -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, Any]]:
    """
    Load constants/keywords from a yaml file

    :param files: list of strings, the file paths to the config/const files
    :param instances: list of Consts, the module paths

    :return: list of keys (str), list of values (Any), list of sources (str),
             list of instances (either Const or Keyword instances)
    """
    # set function name (cannot break here --> no access to inputs)
    func_name = display_func('_load_from_yaml', __NAME__)
    # -------------------------------------------------------------------------
    # load constants from yaml file
    # -------------------------------------------------------------------------
    fvalues, fsources = dict(), dict()
    for filename in files:
        # load the yaml in the standard way
        yaml_dict = base.load_yaml(filename)
        # flatten this dictionary
        flat_dict = base_class.FlatYamlDict(yaml_dict, max_level=3)
        # get key and value pairs
        fkey, fvalue = flat_dict.items()
        # add to fkeys and fvalues (loop around fkeys)
        for it in range(len(fkey)):
            # get this iterations values
            fkeyi, fvaluei = fkey[it], fvalue[it]
            # do not add keys if value is None
            if fvaluei is None:
                continue
            # if this is not a new constant print warning
            if fkeyi in fvalues:
                # log warning message
                wargs = [fkeyi, filename, ','.join(set(fsources)), filename]
                DrsCodedWarning('10-002-00002', 'warning', targs=wargs,
                                func_name=func_name)
            # append to list
            fvalues[fkeyi] = fvaluei
            fsources[fkeyi] = filename
    # -------------------------------------------------------------------------
    # Now need to test the values are correct
    # -------------------------------------------------------------------------
    # storage for returned values
    out_values, out_sources, out_instances = dict(), dict(), dict()
    # loop around modules
    for key in instances:
        if key in fvalues:
            # if we are then we need to validate
            value = instances[key].validate(fvalues[key], source=fsources[key])
            # now append to output lists
            out_values[key] = value
            out_sources[key] = str(fsources[key])
            out_instances[key] = instances[key]
    # return keys values and sources
    return out_values, out_sources, out_instances






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

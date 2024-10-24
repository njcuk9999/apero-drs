#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-09 10:44
@author: ncook
Version 0.0.1
"""
import argparse
import importlib
import os
import string
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple, Union

import numpy as np
import yaml
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.constants import constant_functions
from aperocore import drs_lang
from apero.constants import path_definitions as pathdef
from aperocore.core import drs_exceptions, drs_base_classes, drs_misc

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_installation.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# get colors
Colors = drs_misc.Colors()
# get param dict
ParamDict = param_functions.ParamDict
# define bad characters for profile name (alpha numeric + "_")
BAD_CHARS = [' '] + list(string.punctuation.replace('_', ''))
# Get the text types
textentry = drs_lang.textentry
# -----------------------------------------------------------------------------
HOME = Path('~').expanduser()
DEFAULT_USER_PATH = HOME.joinpath('apero', 'default')
DEFAULT_DATA_PATH = HOME.joinpath('apero', 'data', 'default')

UCONFIG = 'user_config.ini'
UCONST = 'user_constants.ini'

YCONFIG = 'user_config.yaml'
YCONST = 'user_constants.yaml'

OUT_BINPATH = Path('..').joinpath('bin')
OUT_TOOLPATH = Path('..').joinpath('tools')

IN_BINPATH = Path('.').joinpath('recipes', '{0}', '')
IN_TOOLPATH = Path('..').joinpath('apero', 'tools', 'recipes')

ENV_CONFIG = base.USER_ENV
SETUP_PATH = Path('.').joinpath('tools', 'resources', 'setup')

VALIDATE_CODE = Path('bin').joinpath('apero_validate.py')
RESET_CODE = 'apero_reset'
# set descriptions for data paths
DATA_CLASSES = pathdef.BLOCKS
# push into dictionary
DATA_PATHS = dict()
# set cmdline args expected for each
DATA_ARGS = dict()
# loop around data classes and fill data_paths and data_args
for data_class in DATA_CLASSES:
    DATA_PATHS[data_class.key] = [data_class.description, data_class.name]
    DATA_ARGS[data_class.key] = data_class.argname

# set the reset paths (must be checked for empty)
RESET_PATHS = ['DRS_CALIB_DB', 'DRS_TELLU_DB', 'DRS_DATA_RUN']

prompt1 = r"""

# =======================
# COLOURED PROMPT
# =======================
RED="\e[1;31m"
BLUE="\e[1;34m"
YELLOW="\e[0;33m"
WHITE="\e[0;37m"
END="\e[m"
export PS1=" ${YELLOW}{NAME} ${WHITE}\d \t ${BLUE}\u@\h: ${RED}\w${END}\n>>   "
unset RED BLUE YELLOW WHITE END
"""

# define path to language tables
LANG_PATH = 'apero.core.lang.tables'


# =============================================================================
# Define setup/general functions
# =============================================================================
def cprint(message: Union[drs_lang.Text, str], colour: str = 'g'):
    """
    print coloured message

    :param message: str, message to print
    :param colour: str, colour to print
    :return:
    """
    print(Colors.print(str(message), colour))


def ask(question: str, dtype: Union[str, type, None] = None,
        options: Union[List[Any], None] = None,
        optiondesc: Union[List[str], None] = None, default: Any = None,
        required: bool = True, color='g',
        stringlimit: Optional[int] = None) -> Any:
    """
    Ask a question

    :param question: str, the question to ask
    :param dtype: str, the data type (int/float/bool/str/path/YN)
    :param options: list, list of valid options
    :param optiondesc: list, list of option descriptions
    :param default: object, if set the default value, if unset a value
                    if required
    :param required: bool, if False and dtype=path does not create a path
                     else does not change anything
    :param color: str, the color of the text printed out
    :param stringlimit: int, the maximum length of a string

    :return: the response from the user or the default
    """
    # set up check criteria as True at first
    check = True
    # set up user input as unset
    uinput = None
    # -------------------------------------------------------------------------
    # deal with no optionsdesc
    if options is not None:
        if optiondesc is None:
            # TODO: move to langdb
            raise ValueError('Using options but optiondesc not defined')
        if len(optiondesc) != len(options):
            raise ValueError('Using options but optiondesc wrong length')
    # -------------------------------------------------------------------------
    # deal with yes/no dtype
    if isinstance(dtype, str) and dtype.upper() == 'YN':
        options = [drs_lang.YES, drs_lang.NO]
        optiondesc = [drs_lang.YES_OR_NO]
    # deal with paths (expand)
    dcond = isinstance(dtype, str) or isinstance(dtype, Path)
    if dcond and dtype.upper() == 'PATH':
        if default not in ['None', '']:
            default = Path(default)
            default.expanduser()
    # -------------------------------------------------------------------------
    # loop around until check is passed
    while check:
        # ask question
        cprint(question, color)
        # print options
        if options is not None:
            cprint(lang.OPTIONS_ARE + ':', 'b')
            print('   ' + '\n   '.join(list(np.array(optiondesc, dtype=str))))
        if default is not None:
            cprint('   {0}: {1}'.format(lang.DEFAULT_IS, default), 'b')
        # record response
        uinput = input(' >>   ')
        # deal with string ints, floats, logic
        if dtype in ['int', 'float', 'bool']:
            # noinspection PyBroadException
            try:
                basetype = eval(dtype)
                uinput = basetype(uinput)
                check = False
            except Exception as _:
                if uinput == '' and default is not None:
                    check = False
                else:
                    cargs = [dtype]
                    cprint(textentry('40-001-00034', args=cargs), 'y')
                    check = True
                    continue
        # deal with int/float/logic
        if dtype in [int, float, bool, str]:
            # noinspection PyBroadException
            try:
                uinput = dtype(uinput)
                check = False
            except Exception as _:
                cargs = [dtype.__name__]
                cprint(textentry('40-001-00034', args=cargs), 'y')
                check = True
                continue
        # deal with paths
        elif dtype == 'path':
            # --------------------------------------------------------------
            # check whether default wanted and user types 'None' or blank ('')
            if uinput in ['None', ''] and default is not None:
                uinput = default
                # deal with a null default
                if default in ['None', '']:
                    return default
            # deal with case where path is 'None' or blank and path is not
            # required (even if not required must be set to None or blank)
            elif not required and uinput in ['None', '']:
                return None
            # otherwise 'None and '' are not valid
            elif uinput in ['None', '']:
                cprint(textentry('40-001-00035'), 'y')
                check = True
                continue
            # --------------------------------------------------------------
            # try to create path
            # noinspection PyBroadException
            try:
                upath = Path(uinput)
            except Exception as _:
                if not required:
                    cprint(textentry('40-001-00036'), 'y')
                    check = True
                    continue
                else:
                    cprint(textentry('40-001-00037'), 'y')
                    check = True
                    continue
            # get rid of expansions
            upath.expanduser()
            # --------------------------------------------------------------
            # check whether path exists
            if upath.exists():
                return upath
            # if path does not exist ask to make it (if create)
            else:
                # check whether to create path
                pathquestion = textentry('40-001-00038', args=[uinput])
                create = ask(pathquestion, dtype='YN')
                if create:
                    if not upath.exists():
                        # noinspection PyBroadException
                        try:
                            os.makedirs(upath)
                        except Exception as _:
                            cprint(textentry('40-001-00037'), 'y')
                            check = True
                            continue
                    return upath
                else:
                    cprint(textentry('40-001-00037'), 'y')
                    check = True
                    continue
        # deal with Yes/No questions
        elif dtype == 'YN':
            if drs_lang.YES in uinput.upper():
                return True
            elif drs_lang.NO in uinput.upper():
                return False
            else:
                cprint(textentry('40-001-00039', args=[drs_lang.YES_OR_NO]), 'y')
                check = True
                continue
        # deal with options
        if options is not None:
            # convert options to string
            options = np.char.array(np.array(options, dtype=str))
            if str(uinput).upper() in options.upper():
                check = False
                continue
            elif uinput == '' and default is not None:
                check = False
                continue
            else:
                ortxt = ' {0} '.format(lang.OR)
                optionstr = ortxt.join(np.array(options, dtype=str))
                cprint(textentry('40-001-00039', args=[optionstr]), 'y')
                check = True
        # deal with string and string limit
        if dtype == str and stringlimit is not None:
            if len(uinput) > stringlimit:
                msg = 'String length must be less than {0} characters'
                margs = [stringlimit]
                cprint(msg.format(*margs), 'y')
                check = True
                continue
    # deal with returning default
    if uinput == '' and default is not None:
        return default
    else:
        # return uinput
        return uinput


def check_path_arg(name: str, value: Union[str, Path],
                   ask_to_create: bool = True,
                   from_cmd: bool = True) -> Tuple[bool, Path]:
    """
    Check whether path exists and ask user to create it if it doesn't

    :param name: str, the path name (description of the path)
    :param value: str or Path, the path to create
    :param ask_to_create: bool, if True asks user before creation
    :param from_cmd: bool, if True the value is from the command line

    :return: tuple, 1. whether to prompt the user for another path (i.e. they
             didn't want to create the path, 2. the value of the path
    """
    # check if user config is None (i.e. set from cmd line)
    if value is not None:
        # only print this is we are getting the value from cmd
        if from_cmd:
            cprint(textentry('40-001-00040', args=[name, value]))
        # create path
        value = Path(value)
        # check if value exists
        if not value.exists():
            # check whether to create path
            if ask_to_create:
                pathquestion = textentry('40-001-00038', args=[value])
                promptuser = not ask(pathquestion, dtype='YN')
            else:
                promptuser = False
            # make the directory if we are not going to prompt the user
            if not promptuser:
                cprint('\t\tMaking dir {0}: {1}'.format(name, value))
                os.makedirs(value)
        # if path exists we do not need to prompt user
        else:
            promptuser = False
    else:
        promptuser = ask_to_create
    # return prompt usr and value
    return promptuser, value


def user_interface(params: ParamDict, args: argparse.Namespace
                   ) -> Tuple[ParamDict, argparse.Namespace]:
    """
    Ask the user the questions required to install apero

    :param params: ParamDict, the parameter dictionary of constants
    :param args: passed from argparse

    :return: tuple, 1. all parameters dict, 2. the argparse namespace
    """
    # set function name
    func_name = __NAME__ + '.user_interface()'
    # get default from params
    package = params['DRS_PACKAGE']
    # get install yaml
    iparams = base.load_install_yaml()
    user_lang = iparams['LANGUAGE']
    # get available instruments
    drs_instruments = list(np.char.array(params['DRS_INSTRUMENTS']).upper())
    # storage of answers
    all_params = ParamDict()
    # title
    cprint(printheader(), 'm')
    cprint(textentry('40-001-00041', args=[package]), 'm')
    cprint(printheader(), 'm')
    print('\n')
    # ------------------------------------------------------------------
    # add dev mode to allparams
    all_params['DEVMODE'] = getattr(args, 'dev', False)
    # add clean warn
    all_params['CLEANWARN'] = getattr(args, 'clean_no_warning', False)
    # add tar file
    all_params['TARFILE'] = getattr(args, 'tar_file', None)
    # get whether to ask user about creating directories
    askcreate = not getattr(args, 'always_create', True)
    all_params['ASK_CREATE'] = askcreate
    all_params.set_source('ASK_CREATE', func_name)

    # ------------------------------------------------------------------
    # Step 0: Ask for profile name (if not given)
    # ------------------------------------------------------------------
    # deal with having a profile name
    if args.name in ['None', None, '']:
        profilename = ask(textentry('INSTALL_PROFILE_MSG'), str,
                          default='apero')
        # clean profile name
        profilename = clean_profile_name(profilename)
        # update args.name
        args.name = str(profilename).lower()
    else:
        # clean profile name
        profilename = clean_profile_name(args.name)
        # update args.name
        args.name = str(profilename).lower()
    # add name
    all_params['PROFILENAME'] = args.name
    # update default paths
    default_upath = Path(DEFAULT_USER_PATH)
    default_dpath = Path(DEFAULT_DATA_PATH).joinpath(profilename)

    # ------------------------------------------------------------------
    # Step 1: Ask for user config path
    # ------------------------------------------------------------------
    promptuser, userconfig = check_path_arg('config', args.config, askcreate)
    # if we still need to get user config ask user to get it
    if promptuser:
        userconfig = ask(textentry('INSTALL_CONFIG_PATH_MSG'), 'path',
                         default=default_upath)
    # add profile name to userconfig
    userconfig = userconfig.joinpath(profilename)
    # add user config to all_params
    all_params['USERCONFIG'] = userconfig
    args.config = userconfig

    # ------------------------------------------------------------------
    # Step 2: Ask for instrument (from valid instruments)
    # ------------------------------------------------------------------
    user_instrument = getattr(args, 'instrument', 'Null')
    # test if we need instrument
    if user_instrument not in drs_instruments:

        prompt_inst = textentry('40-001-00042')
        inst_options, prompt_options = [], []
        # loop around instruments
        icount, valid_instruments = 1, []
        for it, instrument in enumerate(drs_instruments):
            if instrument.upper() != 'NONE':
                inst_options += [icount]
                prompt_options += ['{0}. {1}'.format(icount, instrument)]
                # add to the counter
                icount += 1
                # add instrument to valid instrument choices
                valid_instruments.append(instrument)
        # ask user
        inst_number = ask(prompt_inst, options=inst_options, dtype='int',
                          optiondesc=prompt_options)
        # update instrument based on inst_number
        instrument = valid_instruments[inst_number - 1]
    else:
        instrument = str(user_instrument)
    # set instrument in all params
    all_params['INSTRUMENT'] = instrument
    all_params.set_source('INSTRUMENT', func_name)
    args.instrument = instrument
    # TODO: set language
    all_params['LANGUAGE'] = user_lang
    all_params.set_source('LANGUAGE', user_lang)
    # ------------------------------------------------------------------
    # add the database settings (and ask user if required
    all_params, args = get_database_settings(all_params, args)
    # ------------------------------------------------------------------
    cprint('\n' + printheader(), 'm')
    cprint(textentry('40-001-00046', args=[instrument]), 'm')
    cprint(printheader(), 'm')
    # ------------------------------------------------------------------
    # set user config
    uconfig = Path(userconfig)
    all_params['USERCONFIG'] = uconfig
    all_params.set_source('USERCONFIG', func_name)
    # make instrument user config directory
    if not uconfig.exists():
        uconfig.mkdir()
    # ------------------------------------------------------------------
    # check data path
    promptuser, datadir = check_path_arg('datadir', args.datadir, askcreate)
    # update args with data dir
    args.datadir = datadir

    # check for data paths in args
    data_prompts, data_values = dict(), dict()
    data_promptuser = False
    for path in DATA_ARGS:
        value = getattr(args, DATA_ARGS[path])
        promptuser1, value = check_path_arg(path, value, askcreate)
        data_prompts[path] = promptuser1
        data_values[path] = value
        data_promptuser |= promptuser1

    # ------------------------------------------------------------------
    # Step 3: Ask for data paths
    # ------------------------------------------------------------------
    if promptuser and data_promptuser:
        advanced = ask(textentry('INSTALL_DATA_PATH_MSG'), dtype='YN')
        cprint(printheader(), 'g')
    else:
        advanced = False
    # ------------------------------------------------------------------
    # if advanced then loop through all options
    if advanced:
        # loop around paths
        for path in DATA_PATHS:
            # get arg value
            promptuser = data_prompts[path]
            argvalue = data_values[path]
            if promptuser:
                # get question and default
                question, default = DATA_PATHS[path]
                defaultpath = default_dpath.joinpath(default)
                # ask question and assign path
                all_params[path] = ask(question, 'path', default=defaultpath)
                all_params.set_source(path, __NAME__)
                # print header
                cprint(printheader(), 'g')
            else:
                all_params[path] = argvalue
                all_params.set_source(path, 'command line')
            # update args
            setattr(args, DATA_ARGS[path], all_params[path])
    # ------------------------------------------------------------------
    elif data_promptuser:
        create = False
        directory = Path(datadir)
        # loop until we have an answer
        while not create:
            if askcreate:
                directory = ask(textentry('40-001-00047'), 'path',
                                default=datadir)
            else:
                directory = datadir
            # ask to create directory
            pathquestion = textentry('40-001-00038', args=[directory])

            if not directory.exists():
                if askcreate:
                    create = ask(pathquestion, dtype='YN')
                else:
                    create = True
                if create:
                    cprint(textentry('40-001-00048', args=directory), 'g')
                    os.makedirs(directory)
            else:
                create = True
        # loop around paths and create them
        for path in DATA_PATHS:
            # get questions and default
            question, default = DATA_PATHS[path]
            # assign path
            dpath = directory.joinpath(default)
            all_params[path] = dpath
            all_params.set_source(path, __NAME__)
            # update args
            setattr(args, DATA_ARGS[path], all_params[path])
            # check whether path exists
            if not dpath.exists():
                cprint(textentry('40-001-00048', args=all_params[path]), 'g')
                os.makedirs(dpath)
        cprint(printheader(), 'g')

    else:
        for path in DATA_PATHS:
            # get questions and default
            question, default = DATA_PATHS[path]
            value = data_values[path]
            if value is None and datadir is not None:
                # create path from datadir
                path_from_datadir = datadir.joinpath(default)
                # add to all params
                all_params[path] = path_from_datadir
                all_params.set_source(path, 'command line + default')
                pargs = [path, all_params[path]]
                # print header
                cprint(textentry('40-001-00049', args=pargs))
                # check path exists
                check_path_arg(path, path_from_datadir, askcreate,
                               from_cmd=False)
            # deal with the case where we have no value and no way to guess it
            elif value is None:
                # raise error as datadir and value are both None
                eargs = [path, DATA_ARGS[path]]
                emsg = ('Cannot create {0}, when using cmd lines args must set'
                        ' either --{1} or --datadir')
                cprint(emsg.format(*eargs), 'red')
                sys.exit()
            # we have a value -- use it
            else:
                # assign path
                all_params[path] = value
                all_params.set_source(path, 'command line')
            # update args
            setattr(args, DATA_ARGS[path], all_params[path])
    # ------------------------------------------------------------------
    # Step 4: Ask for plot mode
    # ------------------------------------------------------------------
    # find value in args
    if args.plotmode is None:
        # ask about plotting, options are 0. (no plots) 1. (plots at end)
        #   2. plots at time of creation
        plot = ask(textentry('40-001-00050'), dtype='int', options=[0, 1, 2, 3],
                   optiondesc=[textentry('40-001-00051'),
                               textentry('40-001-00052'),
                               textentry('40-001-00053'),
                               textentry('40-001-00082')],
                   default=0)
        all_params['DRS_PLOT'] = plot
        all_params.set_source('DRS_PLOT', __NAME__)
        # update args
        args.plotmode = plot
        # add header line
        cprint(printheader(), 'g')
    else:
        cprint(textentry('40-001-00054', args=[args.plotmode]))
        all_params['DRS_PLOT'] = args.plotmode
        all_params.set_source('DRS_PLOT', 'command line')

    # ------------------------------------------------------------------
    # Step 5: Ask whether we want a clean install
    # ------------------------------------------------------------------
    if args.clean is None:
        all_params['CLEAN_INSTALL'] = ask(textentry('INSTALL_CLEAN_MSG'),
                                          dtype='YN')
        all_params.set_source('CLEAN_INSTALL', func_name)
        # update args
        args.clean = all_params['CLEAN_INSTALL']
    else:
        cprint(textentry('40-001-00055', args=[args.clean]))
        all_params['CLEAN_INSTALL'] = eval(args.clean)
        all_params.set_source('CLEAN_INSTALL', 'command line')

    # ------------------------------------------------------------------
    cprint(printheader(), 'm')
    # ----------------------------------------------------------------------
    # return all parameters
    return all_params, args


def get_database_settings(all_params: ParamDict,
                          args: Any) -> Tuple[ParamDict, Any]:
    """
    Ask the user for the database settings

    :param all_params: dict, the user all parameter dictionary
    :param args: args from argparse parser

    :return: dict, the updated all parameter dictionary
    """
    # start a dictionary for database
    all_params['DATABASE'] = dict()
    # ----------------------------------------------------------------------
    # set values to None
    dtype, host, username, password = None, None, None, None
    name, profile = None, None
    # check for parameters in args
    # check type
    if hasattr(args, 'database_type'):
        if args.database_type is not None:
            dtype = str(args.database_type)
    # check host
    if hasattr(args, 'database_host'):
        if args.database_host is not None:
            host = str(args.database_host)
    # check username
    if hasattr(args, 'database_user'):
        if args.database_user is not None:
            username = str(args.database_user)
    # check password
    if hasattr(args, 'database_pass'):
        if args.database_pass is not None:
            password = str(args.database_pass)
    # check database name
    if hasattr(args, 'database_name'):
        if args.database_name is not None:
            name = str(args.database_name)
    # check if any are still None
    prompt_user = False
    if host is None or username is None or password is None:
        prompt_user = True
    if name is None or profile is None:
        prompt_user = True
    # ----------------------------------------------------------------------
    # ask question (if we are prompting user for any option)
    if prompt_user:
        cprint(textentry('INSTALL_DB_MSG'), 'g')
    # ----------------------------------------------------------------------
    if dtype is not None and dtype in base.SUPPORTED_DATABASES:
        response = str(dtype)
    else:
        response = ask(textentry('40-001-00056', args='DATABASE TYPE'),
                       dtype=str, options=base.SUPPORTED_DATABASES,
                       optiondesc=base.SUPPORTED_DATABASES)
    # only add response if not None
    if response not in ['None', '', None]:
        all_params['DATABASE']['TYPE'] = response
        args.database_host = response
    # ----------------------------------------------------------------------
    # ask for the host name
    if host is not None:
        response = str(host)
    # if not set from command line ask user for value
    else:
        response = ask(textentry('40-001-00056', args='HOSTNAME'), dtype=str)
    # only add response if not None
    if response not in ['None', '', None]:
        all_params['DATABASE']['HOST'] = response
        args.database_host = response
    # ----------------------------------------------------------------------
    # ask for the username
    if username is not None:
        response = str(username)
    # if not set from command line ask user for value
    else:
        response = ask(textentry('40-001-00056', args='USERNAME'), dtype=str)
    # only add response if not None
    if response not in ['None', '', None]:
        all_params['DATABASE']['USER'] = response
        args.database_user = response
    # ----------------------------------------------------------------------
    # ask for the password
    if password is not None:
        response = str(password)
    # if not set from command line ask user for value
    else:
        response = ask(textentry('40-001-00056', args='PASSWD'), dtype=str)
    # only add response if not None
    if response not in ['None', '', None]:
        all_params['DATABASE']['PASSWD'] = response
        args.database_pass = response
    # ----------------------------------------------------------------------
    # ask for the database name
    if name is not None:
        response = str(name)
    # if not set from command line ask user for value
    else:
        response = ask(textentry('40-001-00057'), dtype=str)
    # only add response if not None
    if response not in ['None', '', None]:
        all_params['DATABASE']['DATABASE'] = response
        args.database_name = response
    # ----------------------------------------------------------------------
    # Individual database table settings
    all_params, args = database_tables(args, all_params)
    # ----------------------------------------------------------------------
    return all_params, args


def database_tables(args: argparse.Namespace, all_params: ParamDict,
                    db_ask: bool = True
                    ) -> Tuple[ParamDict, argparse.Namespace]:
    """
    Get/ask for the database table names

    :param args: argparse.Namespace - the argparse namespace
    :param all_params: ParamDict, the installation parameter dictionary
    :param db_ask: bool, if True uses default definitions to ask for tables,
                   if False does not ask

    :return: ParamDict, the installation parameter dictionary
    """
    # ----------------------------------------------------------------------
    # Individual database table settings
    # ----------------------------------------------------------------------
    database_user = base.DATABASE_FULLNAMES
    databases_raw = base.DATABASE_NAMES
    if db_ask:
        database_ask = [True, True, False, False, False, False, False]
    else:
        database_ask = [False] * 7
    database_args = ['calibtable', 'tellutable', 'findextable', 'logtable',
                     'astromtable', 'langtable', 'rejecttable']
    # loop around databases
    for db_it in range(len(database_user)):
        # ---------------------------------------------------------------------
        # db key for all_params - capitalized
        dbkey = '{0}_profile'.format(databases_raw[db_it]).upper()
        # ---------------------------------------------------------------------
        # deal with command line arguments
        if hasattr(args, database_args[db_it]):
            # get value
            response = getattr(args, database_args[db_it])
            # only deal with non Null values
            if response not in ['None', '', None]:
                # set key
                all_params['DATABASE'][dbkey] = str(response)
                setattr(args, database_args[db_it], str(response))
                # skip asking the question
                continue
        # ---------------------------------------------------------------------
        # only ask for those flagged as allowed to be changed by user
        if database_ask[db_it] or all_params['DEVMODE']:
            # -----------------------------------------------------------------
            # ask for the database name
            db_qargs = [database_user[db_it], databases_raw[db_it],
                        all_params['PROFILENAME']]
            db_question = textentry('40-001-00058', args=db_qargs)
            # -----------------------------------------------------------------
            response = ask(db_question, dtype=str)
        else:
            response = None
        # --------------------------------------------------------------------
        if response not in ['None', '', None]:
            all_params['DATABASE'][dbkey] = response
            setattr(args, database_args[db_it], response)
        else:
            all_params['DATABASE'][dbkey] = all_params['PROFILENAME']
            setattr(args, database_args[db_it], all_params['PROFILENAME'])
    # ----------------------------------------------------------------------
    return all_params, args


def clean_profile_name(inname: str) -> str:
    """
    Remove any bad characters from profile name

    :param inname: str, the profile name to clean up

    :return: str, the cleaned profile name
    """
    # copy inname
    outname = str(inname.strip())
    # replace bad characters with an underscore
    for bad_char in BAD_CHARS:
        outname = outname.replace(bad_char, '_')
    # replace double underscores
    while '__' in outname:
        outname = outname.replace('__', '_')
    # log that we changed the name (if we did)
    if outname != inname:
        # log warning: Bad profile name changed
        pargs = [inname, outname]
        cprint(textentry('10-002-00007', args=pargs), colour='yellow')
    # return profile name
    return outname


# =============================================================================
# Define installation functions
# =============================================================================
def bin_paths(params: ParamDict, all_params: ParamDict) -> ParamDict:
    """
    Add the bin and tool paths to installation parameter dictionary

    :param params: ParamDict, the constants parameter dictionary
    :param all_params: ParamDict, the installation parameter dictionary

    :return: ParamDict, the updated installation parameter dictionary
    """
    # get package
    package = params['DRS_PACKAGE']
    # get root path
    root = Path(drs_misc.get_relative_folder(package, ''))
    # get out bin path
    out_bin_path = Path(drs_misc.get_relative_folder(package, OUT_BINPATH))
    # get out tools bin path
    out_tool_path = Path(drs_misc.get_relative_folder(package, OUT_TOOLPATH))
    # get tools save location
    in_tool_path = Path(drs_misc.get_relative_folder(package, IN_TOOLPATH))
    # add recipe bin directory to all params
    all_params['DRS_OUT_BIN_PATH'] = out_bin_path
    # add toool directory to all params
    all_params['DRS_OUT_TOOL_PATH'] = out_tool_path
    # add the drs root directory to all params
    all_params['DRS_ROOT'] = root
    # add the individual tool directories to all params
    all_params['DRS_OUT_TOOLS'] = []
    for directory in np.sort(list(in_tool_path.glob('*'))):
        # make out tool paths
        out_tools = out_tool_path.joinpath(directory.name)
        # append out tool paths to drs out tools
        all_params['DRS_OUT_TOOLS'].append(out_tools)
    # return the updated all params
    return all_params


def create_configs(params: ParamDict, all_params: ParamDict) -> ParamDict:
    """
    Create the configuration files and add them to the installation parameter
    dictionary

    :param params: ParamDict, the constants parameter dictionary
    :param all_params: ParamDict, the installation parameter dictionary

    :return: ParamDict, the updated installation parameter dictionary
    """
    # set function name
    func_name = __NAME__ + '.create_configs()'
    # get config directory
    userconfig = all_params['USERCONFIG']
    # get dev mode
    devmode = all_params['DEVMODE']
    askcreate = all_params['ASK_CREATE']
    # deal with language modules
    all_params['LANG_MODULES'] = assign_language_modules(all_params)
    # create install config
    base.create_yamls(all_params)
    # reload dictionaries connected to yaml files
    base.IPARAMS = base.load_install_yaml()
    base.DPARAMS = base.load_database_yaml()
    # make a copy of parameters and update all_params values in them
    uparams = params.copy()
    # push the new keys into uparams
    for key in uparams:
        if key in all_params:
            uparams.set(key, all_params[key], source=params.sources[key],
                        instance=params.instances[key])
    # create user config
    ufiles = create_ufiles(uparams, devmode, askcreate)
    config_lines, const_lines, config_data, const_data = ufiles
    # write / update config and const
    # uconfig = ufile_write(uparams, config_lines, userconfig, UCONFIG,
    #                       'config')
    # uconst = ufile_write(uparams, const_lines, userconfig, UCONST,
    #                      'constant')
    # write the yaml
    yconfig = yfile_write(config_data, userconfig, YCONFIG, 'config')
    yconst = yfile_write(const_data, userconfig, YCONST, 'constant')

    # store filenames in iparams
    # TODO: REPLACE UCONFIG with YCONFIG and same for CONST
    all_params['CONFIGFILES'] = [yconfig, yconst]
    all_params.set_source('CONFIGFILES', func_name)
    # return all_params
    return all_params


def assign_language_modules(all_params: ParamDict) -> List[str]:
    """
    Assign the language modules to use (base on table type and instrument)

    :param all_params: ParamDict, the installation parameter dictionary

    :return: list[str], the list of language modules to use
    """
    # storage of the lang tables to return
    lang_tables = []
    # loop around types of table
    for key1 in ['help', 'text']:
        # loop around the default + instrument
        for key2 in ['default', all_params['INSTRUMENT']]:
            # construct module path
            table = f'{LANG_PATH}.{key2.lower()}_{key1}'
            # add to list of tables
            lang_tables.append(table)
    # return the lang tables
    return lang_tables


def update_configs(all_params: ParamDict) -> ParamDict:
    """
    Update the configuration files and return the installation parameter
    dictionary

    :param all_params: ParamDict, the installation parameter dictionary

    :return: ParamDict, the updated installation parameter dictionary
    """
    # loop around config files
    for filename in all_params['CONFIGFILES']:
        # get the current config values
        fkeys, fvalues = constant_functions.get_constants_from_file(filename)
        fdict = dict(zip(fkeys, fvalues))
        # loop around keys
        for key in fkeys:
            # test if key is new
            if (key in all_params) and (str(all_params[key]) != fdict[key]):
                # update value
                fdict[key] = all_params[key]
        # now update config file
        constant_functions.update_file(filename, fdict)
    # return all parameters
    return all_params


def create_shell_scripts(params: ParamDict, all_params: ParamDict) -> ParamDict:
    """
    Create the shell scripts, copy them to the correct directory and add the
    paths to the installation parameter dictionary

    :param params: ParamDict, the constants parameter dictionary
    :param all_params: ParamDict, the installation parameter dictionary

    :return: ParamDict, the updated installation parameter dictionary
    """
    # ----------------------------------------------------------------------
    # get package
    package = params['DRS_PACKAGE']
    if all_params['PROFILENAME'] not in [None, 'None', '']:
        pname = all_params['PROFILENAME'].replace(' ', '_')
    else:
        pname = package
    # get tools save location
    in_tool_path = Path(drs_misc.get_relative_folder(package, IN_TOOLPATH))
    # ----------------------------------------------------------------------
    # get paths and add in correct order and add bin directory
    paths = [str(all_params['DRS_ROOT'].parent),
             str(all_params['DRS_OUT_BIN_PATH'])]
    # add all the tool directories
    for directory in all_params['DRS_OUT_TOOLS']:
        paths.append(str(directory))
    # ----------------------------------------------------------------------
    # find setup files
    setup_path = Path(drs_misc.get_relative_folder(package, SETUP_PATH))
    # deal with windows
    if os.name == 'nt':
        sep = '";"'
        setup_infiles = ['{0}.win.setup'.format(package.lower())]
        setup_outfiles = ['{0}.win.setup'.format(pname.lower())]
    # deal with unix
    elif os.name == 'posix':
        sep = '":"'
        setup_infiles = ['{0}.bash.setup'.format(package.lower())]
        setup_infiles += ['{0}.sh.setup'.format(package.lower())]
        setup_infiles += ['{0}.zsh.setup'.format(package.lower())]
        setup_outfiles = ['{0}.bash.setup'.format(pname.lower())]
        setup_outfiles += ['{0}.sh.setup'.format(pname.lower())]
        setup_outfiles += ['{0}.zsh.setup'.format(pname.lower())]
    # else generate error message
    else:
        # print error message: Error APERO does not support OS
        eargs = [package, os.name]
        cprint(textentry('00-000-00005', args=eargs), 'red')
        sys.exit()
    # ----------------------------------------------------------------------
    # construct validation code absolute path
    valid_path = in_tool_path.joinpath(VALIDATE_CODE)
    # ----------------------------------------------------------------------
    # setup text dictionary
    text = dict()
    text['ROOT_PATH'] = all_params['DRS_ROOT'].parent
    text['USER_CONFIG'] = all_params['USERCONFIG']
    text['NAME'] = all_params['PROFILENAME']
    text['PATH'] = '"' + sep.join(paths) + '"'
    text['PYTHONPATH'] = '"' + sep.join(paths) + '"'
    # ----------------------------------------------------------------------
    # loop around setup files
    for it, setup_file in enumerate(setup_infiles):
        # deal with having profile name
        if all_params['PROFILENAME'] not in [None, 'None', '']:
            # get absolute path
            inpath = setup_path.joinpath(setup_file + '.profile')
        else:
            # get absolute path
            inpath = setup_path.joinpath(setup_file)
        # get output path
        outpath = all_params['USERCONFIG'].joinpath(setup_outfiles[it])
        # ------------------------------------------------------------------
        # make sure in path exists
        if not inpath.exists():
            # log error: setup file "{0}" does not exist'
            cprint(textentry('00-000-00006', args=[inpath]), 'red')
            sys.exit()
        # ------------------------------------------------------------------
        # make sure out path does not exist
        if outpath.exists():
            os.remove(outpath)
        # ------------------------------------------------------------------
        # read the setup file lines
        with open(inpath, 'r') as f:
            in_lines = f.readlines()
        # ------------------------------------------------------------------
        # loop around lines and update parameters
        out_lines = []
        for in_line in in_lines:
            # construct new line
            out_line = in_line.format(**text)
            # add to new lines
            out_lines.append(out_line)
        # ------------------------------------------------------------------
        # get instrument
        instrument = all_params['INSTRUMENT']
        # add instrument tests
        out_lines.append('\n')
        # run the validation script (just to print splash)
        comment = ('# run the validation script for {0}'
                   ''.format(instrument))
        command = 'python {0}'.format(valid_path)
        # add to out lines
        out_lines.append(comment + '\n')
        out_lines.append(command + '\n')
        # ------------------------------------------------------------------
        # write the lines
        with open(outpath, 'w') as f:
            f.writelines(out_lines)
    # return all params
    return all_params


def clean_install(params: ParamDict, all_params: ParamDict
                  ) -> Union[ParamDict, None]:
    """
    Clean the installation directories and update the installation parameter
    dictionary

    :param params: ParamDict, the constants parameter dictionary
    :param all_params: ParamDict, the installation parameter dictionary

    :return: ParamDict, the updated installation parameter dictionary
    """
    # get package
    package = params['DRS_PACKAGE']
    # get clean warning
    if all_params['CLEANWARN'] is None:
        cleanwarn = False
    elif all_params['CLEANWARN'] in [True, 'True', '1', 1]:
        cleanwarn = True
    else:
        cleanwarn = False
    # get tools save location
    in_tool_path = Path(drs_misc.get_relative_folder(package, IN_TOOLPATH))
    # append tool path
    sys.path.append(str(in_tool_path.joinpath('bin')))
    toolmod = importlib.import_module(RESET_CODE)
    # check if all directories are empty
    cond1 = not reset_paths_empty(all_params)
    cond2 = not all_params['CLEAN_INSTALL']
    # check if user wants a clean install
    if cond1 and cond2:
        return all_params
    # if we are forcing clean install let the user know
    if not cond1:
        cprint(textentry('40-001-00059'), 'y')
    # log that we are performing clean install
    cprint(textentry('40-001-00060'), 'm')
    # add to environment
    add_paths(all_params)
    # construct reset command
    reset_args = toolmod.main(quiet=True, nowarn=cleanwarn, database_timeout=0)
    # deal with a bad reset
    if not reset_args['success']:
        # error message: Error resetting database (see above) cannot install
        #                apero
        cprint(textentry('40-001-00083'), 'r')
        return None
    # return all params
    return all_params


def create_symlinks(params: ParamDict, all_params: ParamDict) -> ParamDict:
    """
    Create the symbolic links in the bin and tools directories and update
    the installation parameter dictionary

    :param params: ParamDict, the constants parameter dictionary
    :param all_params: ParamDict, the installation parameter dictionary

    :return: ParamDict, the updated installation parameter dictionary
    """
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()
    # get package
    package = params['DRS_PACKAGE']
    # get out paths
    out_bin_path = all_params['DRS_OUT_BIN_PATH']
    out_tool_path = all_params['DRS_OUT_TOOL_PATH']
    # get tools save location
    in_tool_path = Path(drs_misc.get_relative_folder(package, IN_TOOLPATH))
    # ------------------------------------------------------------------
    # Copy bin files (for each instrument)
    # ------------------------------------------------------------------
    # log which directory we are populating
    cprint('\n\t Populating {0} directory\n'.format(out_bin_path), 'm')
    # get instrument name
    instrument = all_params['INSTRUMENT']
    # find recipe folder for this instrument
    recipe_raw = Path(str(IN_BINPATH).format(instrument.lower()))
    recipe_dir = Path(drs_misc.get_relative_folder(package, recipe_raw))
    # define suffix
    suffix = '*_{0}.py'.format(instrument.lower())
    # create sym links
    _create_link(recipe_dir, suffix, out_bin_path)

    # ------------------------------------------------------------------
    # Copy tools (do not copy tools directories for instruments not being
    #    installed)
    # ------------------------------------------------------------------
    # get list of tool directories
    dirs = np.sort(list(in_tool_path.glob('*')))

    for directory in dirs:
        # do not copy tools for instruments we are not installing
        # note dirs also has other directories so first need to check
        # we are talking about an instrument directory
        if directory.name.upper() in drs_instruments:
            if directory.name.upper() != instrument:
                continue

        # construct this directories absolute path
        in_tools = in_tool_path.joinpath(directory.name)
        out_tools = out_tool_path.joinpath(directory.name)

        # log which directory we are populating
        cprint(textentry('40-001-00061', args=[out_tools]), 'm')
        # define suffix
        suffix = '*.py'
        # create sym links
        _create_link(in_tools, suffix, out_tools)

    # ------------------------------------------------------------------
    # return all_params
    return all_params


def _create_link(recipe_dir: Path, suffix: Union[str, Path], new_dir: Path,
                 log: bool = True):
    """
    Create a symbolic link

    :param recipe_dir: Path, the directory containing real recipes
    :param suffix: str, the suffix to look for in the original directory
    :param new_dir: Path, the new directory to create link in
    :param log: bool, if True logs creating these new links

    :return: None - creates links in "new_dir"
    """
    # deal with directories not exists
    new_dir.mkdir(parents=True, exist_ok=True)
    # get all python files in recipe folder
    files = np.sort(list(recipe_dir.glob(suffix)))
    # loop around files and create symbolic links in bin path
    for filename in files:
        # get file base name
        basename = filename.name
        # construct new path
        newpath = new_dir.joinpath(basename)
        if log:
            cprint('\t\tMoving {0}'.format(basename))
        # remove link already present
        if newpath.exists() or newpath.is_symlink():
            newpath.unlink()
        # make symlink
        newpath.symlink_to(filename)
        # make executable
        # noinspection PyBroadException
        try:
            newpath.chmod(0o777)
        except Exception as _:
            cprint(textentry('00-000-00007', args=[filename]), 'r')


def add_paths(all_params: ParamDict):
    """
    Add to path and python path (temporarily) while we install apero

    :param all_params: ParamDict, the installation parameter dictionary

    :return: None, just updates PATH and PYTHONPATH environmental variables
    """
    # get paths and add in correct order
    all_paths = [str(all_params['DRS_ROOT'].parent),
                 str(all_params['DRS_OUT_BIN_PATH'])]
    # add all the tool directories
    for directory in all_params['DRS_OUT_TOOLS']:
        all_paths.append(str(directory))
    # make sure we only have unique paths
    all_paths = list(set(all_paths))
    # ----------------------------------------------------------------------
    # set USERCONFIG
    os.environ[ENV_CONFIG] = str(all_params['USERCONFIG'])
    # ----------------------------------------------------------------------
    if os.name == 'posix':
        sep = ':'
    else:
        sep = ';'
    # ----------------------------------------------------------------------
    # add to PATH
    if 'PATH' in os.environ:
        # get old path
        oldpaths = os.environ['PATH'].split(sep)
        oldpaths = list(set(oldpaths))
        # add to paths
        paths = all_paths + oldpaths
        # add to environment
        os.environ['PATH'] = sep.join(paths)
    else:
        # add to environment
        os.environ['PATH'] = sep.join(all_paths)
    # add to PYTHON PATH
    if 'PYTHONPATH' in os.environ:
        oldpaths = os.environ['PYTHONPATH'].split(sep)
        oldpaths = list(set(oldpaths))
        # add to paths
        paths = all_paths + oldpaths
        # add to environment
        os.environ['PYTHONPATH'] = sep.join(paths)
    else:
        # add to environment
        os.environ['PYTHONPATH'] = sep.join(all_paths)


def printheader() -> str:
    """
    Construct a header row the size of the window

    :return: str, the header string to be printed
    """
    rows, columns = param_functions.window_size()
    return '=' * (columns - 1)


def print_options(params: ParamDict, all_params: ParamDict):
    """
    Print the options to run apero

    :param params: ParamDict, the constants parameter dictionary
    :param all_params: ParamDict, the installation parameter dictionary

    :return: None prints to screen (using cprint)
    """
    # set up the text dictionary
    text = dict()
    # deal with user config (should end with os.sep)
    userconfig = str(all_params['USERCONFIG'])
    if not userconfig.endswith(os.sep):
        userconfig += os.sep
    # add to text dictionary
    text['DRS_UCONFIG'] = userconfig
    # add system to text dictionary
    text['SYSTEM'] = '{SYSTEM}'
    # add profile name (package name)
    if all_params['PROFILENAME'] not in ['None', None, '']:
        text['NAME'] = all_params['PROFILENAME']
    else:
        text['NAME'] = params['DRS_PACKAGE']
    # print the messages
    print('\n\n')
    cprint(printheader(), 'm')
    cprint(textentry('40-001-00062', args=[__PACKAGE__]), 'm')
    cprint(printheader(), 'm')
    cprint(textentry('INSTALL_ALIAS_MSG').format(**text), 'g')


def reset_paths_empty(all_params: ParamDict) -> bool:
    """
    Flag whether we need to reset any of the "RESET_PATHS" (global variable)

    :param all_params: ParamDict, the installation parameter dictionary

    :return: bool, True if one of the "RESET_PATHS" is empty, False otherwise
    """
    # look for paths
    for path in RESET_PATHS:
        # get instrument path
        ipath = all_params[path]
        # check for empty
        if len(os.listdir(ipath)) == 0:
            return True
    # if we have got here return False --> none are empty
    return False


# =============================================================================
# create user files functions
# =============================================================================
def create_ufiles(params: ParamDict, devmode: bool, ask_user: bool = True
                  ) -> Tuple[List[str], List[str], CommentedMap, CommentedMap]:
    """
    Create the user config/constant ini files

    :param params: ParamDict, the parameter dictionary of constants
    :param devmode: bool, if True we are in dev mode - need all constants
                    in constants files (not just the normal list of user
                    constants)
    :param ask_user: bool, if True asks the user which constants groups to add
                     (only in dev mode)
    :return: tuple, 1. list of config lines to add to config ini file,
                    2. list of constant lines to add to constant ini file
    """
    # storage of parameters of different types
    config = OrderedDict()
    const = OrderedDict()
    # ------------------------------------------------------------------
    config_groups = []
    const_groups = []
    # ------------------------------------------------------------------
    # dev groups
    dev_groups = dict()
    # flag for all groups
    all_groups = False
    # -----------------------------------------------------------------
    # ask user to add all groups
    if ask_user and not all_groups:
        cprint(printheader(), 'g')
        msg = 'Do you want to add all groups to the config file?'
        umessage = msg
        all_groups = ask(umessage, dtype='YN')
    else:
        all_groups = True
    # ------------------------------------------------------------------
    # loop around all parameters and find which need to be added
    #  to config file and const file
    for param in params:
        # ------------------------------------------------------------------
        # get instance
        instance = params.instances[param]
        # if we don't have instance we continue
        if instance is None:
            continue
        # get group name
        group = instance.group
        # get user variable
        user = instance.user
        # ------------------------------------------------------------------
        # if we have no group we don't want this in config files
        if group is None:
            continue
        # if user if False we don't want this in config files
        if user is False and not devmode:
            continue
        # ------------------------------------------------------------------
        # get source of data
        source = params.sources[param]
        # get config/const
        if 'user_config' in source:
            kind = 'config'
        elif 'default_config' in source:
            kind = 'config'
        elif 'default_constants' in source:
            kind = 'const'
        elif 'user_constants' in source:
            kind = 'const'
        else:
            continue
        # ------------------------------------------------------------------
        # deal with asking the user for groups in devmode
        if devmode and user is False:
            # -----------------------------------------------------------------
            # deal with first time seeing this group
            if group not in dev_groups:
                if all_groups:
                    output = True
                # ask user for output
                elif ask_user:
                    cprint(printheader(), 'g')
                    umessage = textentry('40-001-00063', args=[group, kind])
                    output = ask(umessage, dtype='YN')
                else:
                    output = True
                # add to dev groups
                dev_groups[group] = output
            # else skip if user has choosen that they don't want this group
            if not dev_groups[group]:
                continue
        # ------------------------------------------------------------------
        # add group to group storage (in correct order)
        if kind == 'config' and group not in config_groups:
            config_groups.append(group)
        elif group not in const_groups:
            const_groups.append(group)
        # ------------------------------------------------------------------
        # decide on group
        if kind == 'config':
            if group in config:
                config[group].append([instance, params[param]])
            else:
                config[group] = [[instance, params[param]]]
        elif kind == 'const':
            if group in const:
                const[group].append([instance, params[param]])
            else:
                const[group] = [[instance, params[param]]]
    # ------------------------------------------------------------------
    # TODO: Remove these in favour of the yaml files
    # # create config file
    # config_lines = create_ufile(params['INSTRUMENT'], 'config', config,
    #                             config_groups)
    # # create const file
    # const_lines = create_ufile(params['INSTRUMENT'], 'constant', const,
    #                            const_groups)
    config_lines, const_lines = [], []
    # ------------------------------------------------------------------
    # create config yaml file
    config_data = create_uyaml(params['INSTRUMENT'], 'config', config,
                               config_groups)
    # create const yaml file
    const_data = create_uyaml(params['INSTRUMENT'], 'constant', const,
                              const_groups)
    # ------------------------------------------------------------------
    return config_lines, const_lines, config_data, const_data


def create_uyaml(instrument: str, ckind: str, group_dict: Dict[str, list],
                 grouplist: List[str]) -> CommentedMap:

    # Create a commented map
    data = CommentedMap()
    # Add start comments
    ltitle = '{0} {1} file'.format(instrument, ckind)
    lines = user_header(ltitle, comment='')
    data.yaml_set_start_comment('\n'.join(lines))
    # -------------------------------------------------------------------------
    # define yaml groups from this ckind
    yaml_groups = []
    # loop around groups and get valid groups for this ckind
    for groupstr in grouplist:
        # ---------------------------------------------------------------------
        # get yaml group and group
        yaml_group, group = groupstr.split('.')
        # skip if we've already added this group
        if yaml_group in yaml_groups:
            continue
        # deal with bad group
        if yaml_group not in base.YAML_GROUPS:
            emsg = 'YAML group "{0}" not in base.YAML_GROUPS'
            eargs = [yaml_group]
            raise drs_exceptions.DrsCodedException('', level='error',
                                                   message=emsg.format(*eargs))
        # add to yaml groups
        yaml_groups.append(yaml_group)
        # add a section for this group
        data[yaml_group] = CommentedMap()
        section_lines = ['']
        section_lines += user_header(yaml_group, comment='')
        section_str = '\n'.join(section_lines)
        # push comment for section
        data.yaml_set_comment_before_after_key(yaml_group, before=section_str,
                                               indent=0)
    # loop around groups
    for groupstr in grouplist:
        # ---------------------------------------------------------------------
        # get yaml group and group
        yaml_group, group = groupstr.split('.')
        # ---------------------------------------------------------------------
        # only add if we have parameters that are needed in that group
        if groupstr in group_dict:
            # add a header if this is a new group
            group_lines = ['']
            group_lines += user_header(group, comment='')
            group_str = '\n'.join(group_lines)
            # define section for each group
            data[yaml_group][group] = CommentedMap()
            data[yaml_group].yaml_set_comment_before_after_key(group,
                                                               before=group_str,
                                                               indent=2)
            # loop around group parameters
            for it, item in enumerate(range(len(group_dict[groupstr]))):
                # set lines to add for variable
                var_lines = []
                # get instance of this parameter
                instance = group_dict[groupstr][item][0]
                # get value of this parameter
                value = group_dict[groupstr][item][1]
                name = instance.name
                # create line
                var_lines += instance.write_line(value=value, fmt='yaml')
                # deal with inactive lines - comment them out (with hack)
                if not instance.active:
                    name, value_str = _yaml_inactive_str(name, value)
                # only keep basic types (everything else to string)
                elif not isinstance(value, (int, float, bool, str, list, dict)):
                    value_str = str(value)
                else:
                    value_str = value
                # push into the commented dictionary
                data[yaml_group][group][name] = value_str
                var_str = '\n'.join(var_lines)
                ckw = dict(key=name, before=var_str, indent=4)
                data[yaml_group][group].yaml_set_comment_before_after_key(**ckw)
    # return commented map
    return data


def _yaml_inactive_str(name: str, value: Any) -> Tuple[str, str]:
    """
    Hack for commenting out inactive variables in yaml files
    Also requires a hack before saving the yaml file that replaces
    "^^^" with "\n{indent}" and "+++" with "# "

    :param name: str, the name of the variable
    :param value: any, the value of the variable

    :return: tuple, 1. str, the updated name and 2. the value string
    """
    # our name is going to be commented out: add the +++ in front
    #    this needs replacing before using the yaml file
    name = '+++{0}'.format(name)
    # we don't need to do anything else for simple variables
    if isinstance(value, (int, float, bool, str)):
        return name, value
    # we need a yaml representation of the value (use a dict)
    value_dict = dict()
    # set the key value pair in our temporary dict
    value_dict[name] = value
    # use yaml to dump this variable into a string
    value_str = yaml.dump(value_dict)
    # our yaml string probably ends with a new line remove this (as the
    #   real yaml dump will add this newline in afterwards)
    value_str = value_str.strip('\n')
    # the yaml dump has the variable name followed by ":" remove this as it is
    #    added in the real yaml dump
    value_str = value_str.replace(name + ':', '')
    # value that are list and dictionaries start on new lines which the
    #    yaml will remove so we replace these with a special character
    #    that needs to be replaced back before using
    value_str = value_str.replace('\n', '^^^+++')
    # return the updated name and value string
    return name, value_str


def create_ufile(instrument: str, ckind: str, group_dict: Dict[str, list],
                 grouplist: List[str]) -> List[str]:
    """
    From a dictionary of groups (with constant instances) and a list of groups
    construct a list of lines to add for this "ckind" (constant kind)

    :param instrument: str, the instrument for these constants
    :param ckind: str, the constant kind (either "config" or "constant")
    :param group_dict: dict, a dictionary of groups where each group is a
                       list of tuples where each tuple contains
                       the constants instance and the default value
                       i.e.
                       group_dict['GROUP1'] = group1list

                       group1list = [[constant1, default_value1],
                                     [constant2, default_value2],
                                     [constant3, default_value3]]

    :param grouplist: List of strings, the group names (should be the same as
                      list(grouplist.keys()) but may not be

    :return: List of strings, the lines to add to the "ckind" ini file
    """
    lines = []
    ltitle = '{0} {1} file'.format(instrument, ckind)
    lines += user_header(ltitle, comment='# ')
    # loop around groups
    for group in grouplist:
        # only add if we have parameters that are needed in that group
        if group in group_dict:
            # add a header if this is a new group
            lines += ['']
            lines += user_header(group, comment='# ')
            # loop around group parameters
            for item in range(len(group_dict[group])):
                # get instance of this parameter
                instance = group_dict[group][item][0]
                # get value of this parameter
                value = group_dict[group][item][1]
                # create line
                lines += instance.write_line(value=value)
    # return lines
    return lines


def user_header(title: str, comment: str = '# ') -> List[str]:
    """
    Returns a group title for constants / config ini file

    :param title: str, the group title
    :param comment: str, the comment character to use

    :return: List of strings - the title lines to add
    """
    lines = ['{0}{1}'.format(comment, '-' * 77),
             '{0} {1}'.format(comment, title),
             '{0}{1}'.format(comment, '-' * 77)]
    return lines


def ufile_write(aparams: ParamDict, lines: List[str], upath: Path,
                ufile: Union[Path, str], ckind: str) -> Path:
    """
    Write a constants/config ini file to disk

    :param aparams: ParamDict, the installation parameter dictionary
    :param lines: list of strings, the list of lines to be added to the ini
                  file
    :param upath: Path, the directory and full path of the user ini file to be
                  written
    :param ufile: Path, the filename for the user ini file (this should be
                  different depending on "ckind") otherwise files will overwrite
                  each other
    :param ckind: str, the constant kind (either "config" or "constant") for the
                  user ini file

    :return: Path, the full path and filename to the user ini file
    """
    # make directory if it doesn't exist
    if not upath.exists():
        os.makedirs(upath)
    # ----------------------------------------------------------------------
    # define config file path
    ufilepath = upath.joinpath(ufile)
    # ----------------------------------------------------------------------
    # deal with config file existing
    if ufilepath.exists():
        # read the lines
        with ufilepath.open('r') as u_file:
            current_lines = u_file.readlines()
        # now need to check these lines against lines
        for l_it, line in enumerate(lines):
            # we shouldn't worry about old comment lines
            if line.strip().startswith('#'):
                continue
            if len(line) == 0:
                continue
            # get variable name
            variable, value = line.split('=')
            variable = variable.strip()
            value = value.strip()
            cvalue, cline = None, ''
            # do not correct variables that we will automatically set later
            #   ( set by user)
            if variable in aparams:
                continue
            # loop around current lines
            for c_it, cline in enumerate(current_lines):
                if cline.strip().startswith('#'):
                    continue
                if len(cline) == 0:
                    continue
                if variable in cline:
                    cvariable, cvalue = cline.split('=')
                    cvariable = cvariable.strip()
                    cvalue = cvalue.strip().strip('\n')
                    # only if we have a matching variable
                    if cvariable == variable:
                        break
            # if line is the same we continue
            if value == cvalue:
                continue
            # deal with line found
            elif cvalue is not None:
                # display a warning
                cargs = [ckind, variable]
                cprint(textentry('40-001-00064', args=cargs), 'y')
                cargs = [value, cvalue]
                output = ask(textentry('40-001-00065', args=cargs), dtype='YN')
                if output:
                    lines[l_it] = cline
    # ----------------------------------------------------------------------
    # write files
    with ufilepath.open('w') as u_file:
        for line in lines:
            if not line.endswith('\n'):
                u_file.write(line + '\n')
            else:
                u_file.write(line)
    # return user file path
    return ufilepath


def yfile_write(data: CommentedMap, upath: Path, ufile: Union[Path, str],
                ckind: str) -> Path:
    # initialize YAML object
    yaml_inst = YAML()
    # make directory if it doesn't exist
    if not upath.exists():
        os.makedirs(upath)
    # ----------------------------------------------------------------------
    # define config file path
    ufilepath = upath.joinpath(ufile)
    # ----------------------------------------------------------------------
    # deal with yaml file existing
    if ufilepath.exists():
        # read the lines
        current_data = base.load_yaml(str(ufilepath))
        # flatten current data
        current_dict = drs_base_classes.FlatYamlDict(current_data)
        # flatten data
        data_dict = drs_base_classes.FlatYamlDict(data)
        # now need to check these lines against lines
        for key in current_dict:
            # deal with old keys not existing in new data
            if key not in data_dict:
                continue
            # deal with matching keys (skip) - deal with string representations
            #    as these should match
            if str(data_dict[key]) == str(current_dict[key]):
                continue
            # get the path in non-flat dictionary
            path = current_dict.key_dict[key]
            # assume we have a section a group and name for the key
            section, group, name = path
            # display a warning
            cargs = [ckind, '.'.join(path)]
            cprint(textentry('40-001-00064', args=cargs), 'y')
            cargs = [data_dict[key], current_dict[key]]
            output = ask(textentry('40-001-00065', args=cargs), dtype='YN')
            # update the key if required
            if output:
                data[section][group][name] = current_dict[key]
    # ----------------------------------------------------------------------
    # write files
    with ufilepath.open('w') as y_file:
        yaml_inst.dump(data, y_file)
    # ----------------------------------------------------------------------
    # hack replace +++ with #
    with open(ufilepath, 'r') as ofile:
        lines = ofile.readlines()
        for it, line in enumerate(lines):
            # +++ is a special character that needs to be replaced back
            #   it represents a commented line
            line = line.replace('+++', '# ')
            # ^^^ is a special character that needs to be replaced back
            #   it represents a newline indent=4
            line = line.replace('^^^', '\n    ')
            # update line in list
            lines[it] = line
    with open(ufilepath, 'w') as ofile:
        ofile.writelines(lines)
    # ----------------------------------------------------------------------
    # return user file path
    return ufilepath


# =============================================================================
# update functions
# =============================================================================
def update(params: ParamDict, args: argparse.Namespace) -> ParamDict:
    """
    Get parameters from "params" and from the current setup and the input
    arguments and construct the installation parameter dictionary from here
    (instead of asking for user for all parameters)

    :param params: ParamDict, the parameter dictionary of constants
    :param args: argparse.Namespace - command line arguments passed via argparse

    :return: ParamDict, the installation parameter dictionary
    """
    # set function name
    func_name = __NAME__ + '.update()'
    # get config path
    config_env = params['DRS_USERENV']
    # check for config environment set
    config_path = os.getenv(config_env)
    # deal with no config path set
    if config_path is None:
        cprint(textentry('00-000-00008'), 'r')
        sys.exit()
    else:
        config_path = Path(config_path)
    # ----------------------------------------------------------------------
    # find all installed instruments
    instrument = base.IPARAMS['INSTRUMENT']
    language = base.IPARAMS['LANGUAGE']
    # ----------------------------------------------------------------------
    # set up dictionary
    all_params = ParamDict()
    # ------------------------------------------------------------------
    # add dev mode to allparams
    all_params['DEVMODE'] = getattr(args, 'devmode', False)
    # add clean warn
    all_params['CLEANWARN'] = getattr(args, 'cleanwarn', False)
    # add tar file
    all_params['TARFILE'] = getattr(args, 'tar_file', None)
    # get whether to ask user about creating directories
    askcreate = not getattr(args, 'always_create', True)
    all_params['ASK_CREATE'] = askcreate
    # ----------------------------------------------------------------------
    # deal with having a profile name
    if args.name in ['None', None, '']:
        profilename = ask(textentry('INSTALL_PROFILE_MSG'), str,
                          default='apero')
        # clean profile name
        profilename = clean_profile_name(profilename)
        # update args.name
        args.name = str(profilename).lower()
    else:
        # clean profile name
        profilename = clean_profile_name(args.name)
        # update args.name
        args.name = str(profilename).lower()
    # add name
    all_params['PROFILENAME'] = args.name
    # ------------------------------------------------------------------
    # add user config
    all_params['USERCONFIG'] = config_path
    all_params.set_source('USERCONFIG', func_name)
    # set instrument in all params
    all_params['INSTRUMENT'] = instrument
    all_params.set_source('INSTRUMENT', func_name)
    all_params['LANGUAGE'] = language
    all_params.set_source('LANGUAGE', language)
    # load params for instrument
    iparams = load_functions.load_config(select.INSTRUMENTS, cache=False)
    # ------------------------------------------------------------------
    # loop around data paths
    for datapath in DATA_PATHS.keys():
        # get data paths
        all_params[datapath] = Path(iparams[datapath])
        all_params.set_source(datapath, iparams.sources[datapath])
    # ------------------------------------------------------------------
    # add clean install
    if args.clean in ['True', True, '1', 1]:
        all_params['CLEAN_INSTALL'] = True
        all_params.set_source('CLEAN_INSTALL', 'sys.argv')
    else:
        all_params['CLEAN_INSTALL'] = False
        all_params.set_source('CLEAN_INSTALL', func_name)
    # ------------------------------------------------------------------
    # setup a database dictionary
    all_params['DATABASE'] = dict()
    # Individual database table settings
    all_params, args = database_tables(args, all_params, db_ask=False)
    # ------------------------------------------------------------------
    # update base.PARAMS with all params
    base.DPARAMS = update_dparams(all_params, base.DPARAMS)
    # ------------------------------------------------------------------
    # add the current database
    all_params = update_db_settings(all_params)
    # ------------------------------------------------------------------
    # return all params
    return all_params


def update_dparams(aparams: ParamDict,
                   dparams: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the database dictionary, this is required so we can then pass it to
    the normal function - but with database parameters updated from "aprams"
    (the installation parameter dictionary)

    :param aparams: ParamDict, the installation parameter dictionary
    :param dparams: dict, the database dictionary (base.DPARAMS)

    :return: dict, the base.DPARAMS (normally this should be returned to
             update base.DPARAMS - but this is left to the function call
             incase it is required in other situations
    """
    # loop around databases
    for dbname in base.DATABASE_NAMES:
        dbkey = f'{dbname}_profile'.upper()
        value = aparams['DATABASE'].get(dbkey, None)
        if value is not None:
            dparams[dbname.upper()]['PROFILE'] = value
    # return dparams
    return dparams


def update_db_settings(aparams: ParamDict) -> ParamDict:
    """
    Update "aparams" (the installation parameter dictionary) with the database
    settings from base.DPARAMS

    :param aparams: ParamDict, the installation parameter dictionary

    :return: ParamDict, the updated installation parameter dictionary
    """
    # read the database settings for current profile
    dparams = base.DPARAMS
    # ------------------------------------------------------------------
    # Database Settings
    # ------------------------------------------------------------------
    aparams['DATABASE'] = dict()
    # add database settings
    aparams['DATABASE']['HOST'] = dparams['HOST']
    aparams['DATABASE']['USER'] = dparams['USER']
    aparams['DATABASE']['PASSWD'] = dparams['PASSWD']
    aparams['DATABASE']['DATABASE'] = dparams['DATABASE']
    aparams['DATABASE']['TYPE'] = dparams['TYPE']
    # add database parameters
    # loop around databases
    for dbname in base.DATABASE_NAMES:
        # yaml is upper case
        ydbname = dbname.upper()
        # get correct dictionary
        sdict = dparams[ydbname]
        # add calib database
        aparams['DATABASE'][f'{ydbname}_NAME'] = sdict['NAME']
        if 'RESET' in sdict:
            aparams['DATABASE'][f'{ydbname}_RESET'] = sdict['RESET']
        aparams['DATABASE'][f'{ydbname}_PROFILE'] = sdict['PROFILE']
    # ------------------------------------------------------------------
    # return the update all_params
    return aparams


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
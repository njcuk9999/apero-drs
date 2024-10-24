#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-18 at 12:05

@author: cook
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

from aperocore.base import base
from aperocore import drs_lang
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from aperocore.core import drs_text


# =============================================================================
# Define variables
# =============================================================================
__PATH__ = Path(__file__).parent.parent
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
class SetupArgument:
    def __init__(self, name: str, argname: str = None,
                 default_value: Any = None, dtype: str = 'str',
                 helpstr: str = None,
                 options: List[Any] = None, required: bool = False,
                 depends: str = None, sets: Dict[str, Any] = None,
                 ask: bool = True, restricted_chars: List[str] = None,
                 alt_argnames: List[str] = None,
                 stringlimit: int = None, qstr: str = None,
                 optiondescs: List[str] = None,
                 aperoname: str = None,
                 installname: str = None,
                 databasename: str = None):
        """
        Setup argument class

        :param name: str, the name of the argument
        :param default_value: Any, the default value of the argument
        :param dtype: type, the data type of the argument
        :param helpstr: str, the help string for the argument
        :param options: list of Any, the options for the argument
        :param required: bool, whether the argument is required
        :param depends: str, only ask for this argument  if this argument is
                        not given (None)
        :param sets: dict, dictionary of arguments to set if this argument is
                     given (i.e. a directory path setting sub-directories)
        :param ask: bool, whether to ask for this argument when using the
                    user interface
        :param alt_argnames: str, alternative argument names
        :param stringlimit: int, the maximum length of a string
        :param qstr: str, the question string to ask the user (if None uses
                     the help string)
        :param optiondescs: list of str, the descriptions of the options
        """
        # set name for argument
        self.name = name
        # set argparse name for argument
        if argname is None:
            self.argname = '--' + name.strip().replace(' ', '_')
        else:
            self.argname = argname
        # set default value
        self.default_value = default_value
        # set the dtype
        self.dtype = dtype
        # set the help string
        if helpstr is None:
            self.helpstr = 'Set the {0} parameter'.format(name)
        else:
            self.helpstr = helpstr
        # ---------------------------------------------------------------------
        # set the options
        self.options = options
        # set the option descriptions
        self.optiondescs = optiondescs
        # deal with option desc set (add to helpstr)
        if self.options is not None and self.optiondescs is not None:
            # storage for option strings
            option_strings = []
            # loop around options
            for option, desc in zip(self.options, self.optiondescs):
                # add to option strings
                option_strings.append('{0}={1}'.format(option, desc))
            # add to help string
            self.helpstr += ' Options: {0}'.format(', '.join(option_strings))
        # ---------------------------------------------------------------------
        # set whether required (not allowed to be None by the end of setup)
        self.required = required
        # set whether this argument depends on another argument being set
        self.depends = depends
        # set which argument this argument can set (dictionary of arguments)
        self.sets = sets
        # whether to ask the user for this constant
        self.ask = ask
        # sets which characters are not allowed in the argument
        if restricted_chars is None:
            self.restricted_chars = []
        else:
            self.restricted_chars = restricted_chars
        # set alternative argument names
        if alt_argnames is None:
            self.alt_argnames = []
        else:
            self.alt_argnames = alt_argnames
        # set the string limit
        self.stringlimit = stringlimit
        # set the question string
        self.question_string = qstr
        # store the apero name
        self.apero_name = aperoname
        # store the install name
        self.install_name = installname
        # store the database name
        self.database_name = databasename

    def parser_args(self) -> List[Any]:
        # storage for arguments
        args = []
        # add the argument name
        args.append(self.argname)
        # add alternative argument names
        for argname in self.alt_argnames:
            args.append(argname)
        # return the args
        return args

    def parser_kwargs(self) -> Dict[str, Any]:
        # storage for kwargs
        kwargs = dict()
        # set the default value to None - we never set this from command line
        kwargs['default'] = None
        # set the destination
        kwargs['dest'] = self.name
        # set the help string
        kwargs['help'] = self.helpstr
        # set the parser action
        if self.dtype in [bool, 'bool']:
            kwargs['action'] = 'store_true'
            return kwargs
        else:
            kwargs['action'] = 'store'
        # deal with type
        typetrans = dict(zip(base.SIMPLE_STYPES, base.SIMPLE_TYPES))
        if self.dtype is not None:
            if self.dtype in typetrans:
                kwargs['type'] = typetrans[self.dtype]
            else:
                kwargs['type'] = str
        # set the choices
        if self.options is not None:
            # add the choices
            kwargs['choices'] = self.options
        # return the kwargs
        return kwargs


def catch_sigint(signal_received: Any, frame: Any):
    """
    Catch sigint signal
    """
    # we don't use these we just exit
    _ = signal_received, frame
    # print: Exiting installation script
    drs_log.AperoCodedException('40-001-00075')
    # raise Keyboard Interrupt
    sys.exit(0)


def command_line_args(sargs: Dict[str, SetupArgument]) -> ParamDict:
    # install description
    description = textentry('INSTALL_DESCRIPTION')
    # start the parser
    parser = argparse.ArgumentParser(description=description.format(__PATH__))
    # loop around arguments
    for argname in sargs:
        # get this argument
        arg = sargs[argname]
        # add argument to parser
        parser.add_argument(*arg.parser_args(), **arg.parser_kwargs())
    # get unused arguments
    _, remaining = parser.parse_known_args()
    # parse arguments
    raw_params = vars(parser.parse_args())
    # storage for params
    params = ParamDict()

    used = []
    # loop around arguments
    for argname in sargs:
        # if we have used argument (due to a set) skip this argument
        if argname in used:
            continue
        # get arg instance
        arg = sargs[argname]
        # get value
        value = raw_params[argname]

        # if command line argument is None we use the default value
        if value is None:
            params.set(argname, arg.default_value, source='default')
        # if value is different from default source is the command line
        else:
            if arg.restricted_chars:
                for char in arg.restricted_chars:
                    if char in value:
                        # print error message
                        emsg = 'Restricted character "{0}" in argument={1}'
                        eargs = [char, argname]
                        raise drs_log.AperoCodedException(None, message=emsg,
                                                          targs=eargs)
            if arg.argname in remaining:
                params.set(argname, value, source='default')
            else:
                params.set(argname, value, source='command_line')
        # keep track of processed argnames
        used.append(argname)
        # deal with set
        if params.sources[argname] == 'command_line' and arg.sets is not None:
            # loop around sets
            for key in arg.sets:
                # get the value
                value = arg.sets[key].format(**params)
                # update value in params
                params.set(key, value, source=f'set[{arg.name}]')
                # keep track of processed argnames
                used.append(key)

    # -------------------------------------------------------------------------
    # specific arguments
    params = fix_config_path(params)


    # return params
    return params


def ask_user(params: ParamDict, sargs: Dict[str, SetupArgument]) -> ParamDict:
    
    # loop around all arguments
    for argname in sargs:
        # get this argument
        arg = sargs[argname]
        # ---------------------------------------------------------------------
        # if we don't need to ask for this argument then continue
        if not arg.ask:
            continue
        # ---------------------------------------------------------------------
        # don't ask about the arg if depends is set and variable is not None
        if arg.depends is not None:
            if arg.depends in params and params[arg.depends] is not None:
                continue
        # ---------------------------------------------------------------------
        # get the value from params
        value = params[arg.name]
        # get the source of the value
        source = params.sources[arg.name]
        # ---------------------------------------------------------------------
        # if source is command line we skip this argument - we don't need to ask
        if source == 'command_line':
            msg = '{0}="{1}" from command line [{2}]'
            margs = [arg.argname, value, argname.upper()]
            drs_text.cprint(msg.format(*margs), 'magenta')
            continue
        # ---------------------------------------------------------------------
        # Deal with boolean dtype
        if arg.dtype.lower() == 'bool':
            dtype = 'yn'
        elif arg.dtype.lower() == 'path':
            dtype = 'path'
        else:
            dtype = arg.dtype
        # ---------------------------------------------------------------------
        # construct the question for the user
        if arg.question_string is not None:
            qargs = [arg.question_string, argname.upper()]
            question = '{0} [{1}]'.format(*qargs)
        else:
            # get the help string
            qhelpstr = arg.helpstr.lower()
            # deal with starting with "the"
            if qhelpstr.startswith('the'):
                qargs = [qhelpstr, argname.upper()]
                question = 'Define {0} [{1}]'.format(*qargs)
            # deal with starting with "set"
            elif qhelpstr.startswith('set'):
                qhelpstr = qhelpstr[3:]
                qargs = [qhelpstr, argname.upper()]
                question = 'Set {0} [{1}]'.format(*qargs)
            # deal with starting with "edit"
            elif qhelpstr.startswith('edit'):
                qhelpstr = qhelpstr[4:]
                qargs = [qhelpstr, argname.upper()]
                question = 'Edit {0} [{1}]'.format(*qargs)
            # deal with all other cases
            else:
                qargs = [qhelpstr, argname.upper()]
                question = 'Define the {0} [{1}]'.format(*qargs)
        # ---------------------------------------------------------------------
        # get the user input
        uinput = user_input(question, dtype=dtype.lower(),
                            default=value,
                            required=arg.required,
                            options=arg.options,
                            optiondescs=arg.optiondescs,
                            stringlimit=arg.stringlimit,
                            restricted_chars=arg.restricted_chars)
        # update value in params
        params.set(arg.name, uinput, source='user_input')
        # deal with set
        if uinput is not None and arg.sets is not None:
            # loop around sets
            for key in arg.sets:
                # get the value
                value = arg.sets[key].format(**params)
                # update value in params
                params.set(key, value, source=f'set[{arg.name}')
    # -------------------------------------------------------------------------
    # specific arguments
    params = fix_config_path(params)
    # -------------------------------------------------------------------------
    return params


def update_setup(setup_params: ParamDict,
                 sargs: Dict[str, SetupArgument]) -> ParamDict:

    # if we have a environment variable we can get current parameters from
    # the setup directory
    cond1 = 'DRS_UCONFIG' in os.environ
    cond2 = setup_params['NAME'] is not None
    cond3 = setup_params['CONFIG_PATH'] is not None
    # ----------------------------------------------------------------------
    # Get the config path
    # ----------------------------------------------------------------------
    if (not cond1) and not (cond2 and cond3):
        emsg = ('Cannot update setup without DRS_UCONFIG environment variable '
                'set or --name and --config arguments set')
        raise drs_log.AperoCodedException(None, message=emsg)
    elif cond1:
        # get the config path
        config_path = os.environ['DRS_UCONFIG']
    else:
        # get the config path
        config_path = setup_params['CONFIG_PATH']
        # lets set this in os.envinron
        os.environ['DRS_UCONFIG'] = config_path
    # ----------------------------------------------------------------------
    # Once DRS_UCONFIG is set we can load the parameters
    # ----------------------------------------------------------------------
    from apero.instruments import select
    # get the current apero parameters
    aparams = load_functions.load_config(select.INSTRUMENTS)
    # get the current install parameters
    iparams = base.load_yaml(os.path.join(config_path, 'install.yaml'))
    # get the current database parameters
    dparams = base.load_yaml(os.path.join(config_path, 'database.yaml'))
    # access dparams using paths
    dparam2path = param_functions.base_class.Path2Dict(dparams)
    # ----------------------------------------------------------------------
    # Update the setup parameters
    for argname in sargs:
        # if the argument is not in the setup parameters we skip
        if argname not in setup_params:
            continue
        # get the apero name, install name and database name
        apero_name = sargs[argname].apero_name
        install_name = sargs[argname].install_name
        database_name = sargs[argname].database_name
        # if the key is in the apero parameters we update the setup parameters
        if apero_name is not None and apero_name in aparams:
            value = aparams[apero_name]
            setup_params.set(argname, value, source='apero.params')
            msg = '{0}="{1}" from apero params [{2}]'
            margs = [apero_name, value, argname.upper()]
            drs_text.cprint(msg.format(*margs), 'magenta')
        # if the key is in the install parameters we update the setup parameters
        if install_name is not None and install_name in iparams:
            value = iparams[install_name]
            setup_params.set(argname, value, source='apero.iparams')
            msg = '{0}="{1}" from install params [{2}]'
            margs = [install_name, value, argname.upper()]
            drs_text.cprint(msg.format(*margs), 'magenta')
        # if the key is in the database parameters we update the setup parameters
        if database_name is not None and database_name in dparam2path:
            # get value from a path
            value = dparam2path[database_name]
            setup_params.set(argname, value, source='apero.dparams')
            msg = '{0}="{1}" from database params [{2}]'
            margs = [database_name, value, argname.upper()]
            drs_text.cprint(msg.format(*margs), 'magenta')
    # -------------------------------------------------------------------------
    # return the updated setup parameters
    return setup_params


def run_setup(params: ParamDict):
    pass


# =============================================================================
# Define other functions
# =============================================================================
def fix_config_path(params: ParamDict) -> ParamDict:
    """
    Fix the config path (make sure it ends with the name)

    :param params: ParamDict, the parameters to fix

    :return params: ParamDict, the fixed parameters
    """
    # only do this if we have both the name and config_path
    if params['NAME'] is not None and params['CONFIG_PATH'] is not None:
        # make sure config_path ends with the name
        if not params['CONFIG_PATH'].endswith(params['NAME']):
            # add the name to the end of the config_path
            config_path = os.path.join(params['CONFIG_PATH'], params['NAME'])
            # update parmaeters
            params.set('CONFIG_PATH', config_path, source='command_line')
            # need to make sure this exists
            if not os.path.exists(config_path):
                os.makedirs(config_path)
    # return parameters (updated or not)
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

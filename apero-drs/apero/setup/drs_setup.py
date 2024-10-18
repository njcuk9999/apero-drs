#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-18 at 12:05

@author: cook
"""
import argparse
import string
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from aperocore import drs_lang
from aperocore.constants import param_functions
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
# all punctuation except underscore + whitespaces
EXC_CHARS = string.punctuation.replace('_', ' ').split()
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
                 stringlimit: int = None, qstr: str = None):
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
        # set the options
        self.options = options
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
        # set the parser action
        if self.dtype == bool:
            kwargs['action'] = 'store_true'
        else:
            kwargs['action'] = 'store'
        # set the default value to None - we never set this from command line
        kwargs['default'] = None
        # set the destination
        kwargs['dest'] = self.name
        # set the help string
        kwargs['help'] = self.helpstr
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


def command_line_args() -> ParamDict:
    # install description
    description = textentry('INSTALL_DESCRIPTION')
    # start the parser
    parser = argparse.ArgumentParser(description=description.format(__PATH__))
    # loop around arguments
    for argname in SARGS:
        # get this argument
        arg = SARGS[argname]
        # add argument to parser
        parser.add_argument(*arg.parser_args(), **arg.parser_kwargs())
    # parse arguments
    raw_params = vars(parser.parse_args())
    # storage for params
    params = ParamDict()
    # loop around arguments
    for argname in SARGS:
        # if value is different from default source is the command line
        if raw_params[argname] != SARGS[argname].default_value:
            params.set(argname, raw_params[argname], source='command_line')
        # otherwise source is the default value
        else:
            params.set(argname, SARGS[argname].default_value, source='default')
    # return params
    return params


def ask_user(params: ParamDict) -> ParamDict:
    
    # loop around all arguments
    for arg in SARGS:
        # get this argument
        arg = SARGS[arg]
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
            qargs = [arg.question_string, arg.name]
            question = '{0} [{1}]'.format(*qargs)
        else:
            qargs = [arg.helpstr.lower(), arg.name]
            question = 'Define the {0} [{1}]'.format(*qargs)
        # get the user input
        uinput = user_input(question, dtype=dtype.lower(),
                            default=value,
                            required=arg.required,
                            options=arg.options,
                            stringlimit=arg.stringlimit)
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

    return params


def update_setup(params: ParamDict):
    pass


def run_setup(params: ParamDict):
    pass


# =============================================================================
# Define setup arguments
# =============================================================================
SARGS = dict()
# APERO profile name
SARGS['name'] = SetupArgument(name='name', argname='--name',
                              default_value=None, dtype='str',
                              required=True,
                              helpstr='The name of the apero profile to create',
                              restricted_chars=EXC_CHARS)
# whether we are updating the current profile or creating a new one
SARGS['update'] = SetupArgument(name='update', argname='--update',
                                default_value=False, dtype='bool', ask=False,
                                helpstr='whether to update current profile')
# the path where the user config files for this apero profile will be stored
SARGS['config_path'] = SetupArgument(name='config_path', argname='--config',
                                     default_value=None, dtype='path',
                                     required=True,
                                     helpstr='The path to the user config '
                                             'directory for this apero profile')
# The instrument we are installing apero for
SARGS['INSTRUMENT'] = SetupArgument(name='INSTRUMENT', argname='--instrument',
                                    default_value=None,
                                    dtype='str', options=INSTRUMENTS,
                                    required=True,
                                    helpstr='The instrument to use')
# -----------------------------------------------------------------------------
# Directory settings
# -----------------------------------------------------------------------------
# The data source we are installing apero for
SARGS['DATADIR'] = SetupArgument(name='DATADIR', argname='--datadir',
                                 default_value=None, dtype='path',
                                 helpstr='The data directory to use (do not '
                                         'set if setting directories '
                                         'separately)',
                                 qstr='Define the data directory to use '
                                      '(leave blank to set directories '
                                      'separately)',
                                 sets=dict(RAWDIR='{DATADIR}/raw',
                                           TMPDIR='{DATADIR}/tmp',
                                           REDDIR='{DATADIR}/red',
                                           CALDIR='{DATADIR}/calib',
                                           TELDIR='{DATADIR}/tellu',
                                           OUTDIR='{DATADIR}/out',
                                           LBLDIR='{DATADIR}/lbl',
                                           LOGDIR='{DATADIR}/log',
                                           PLOTDIR='{DATADIR}/plot',
                                           RUNDIR='{DATADIR}/run',
                                           ASSETSDIR='{DATADIR}/assets',
                                           OTHERDIR='{DATADIR}/other'
                                           ))
# The raw data directory to use (if not using DATADIR)
SARGS['RAWDIR'] = SetupArgument(name='RAWDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The raw data directory to use')
# The tmp data directory to use (if not using DATADIR)
SARGS['TMPDIR'] = SetupArgument(name='TMPDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The tmp data directory to use')
# The reduced data directory to use (if not using DATADIR)
SARGS['REDDIR'] = SetupArgument(name='REDDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The reduced data directory to use')
# the calibration directory to use (if not using DATADIR)
SARGS['CALDIR'] = SetupArgument(name='CALDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The calibration data directory to use')
# the telluric directory to use (if not using DATADIR)
SARGS['TELDIR'] = SetupArgument(name='TELDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The telluric data directory to use')
# the out directory to use (if not using DATADIR)
SARGS['OUTDIR'] = SetupArgument(name='OUTDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The out directory to use')
# the lbl directory to use (if not using DATADIR)
SARGS['LBLDIR'] = SetupArgument(name='LBLDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The lbl directory to use')
# the log directory to use (if not using DATADIR)
SARGS['LOGDIR'] = SetupArgument(name='LOGDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The log directory to use')
# the plot directory to use (if not using DATADIR)
SARGS['PLOTDIR'] = SetupArgument(name='PLOTDIR', default_value=None,
                                 dtype='path', required=True, depends='DATADIR',
                                 helpstr='The plot directory to use')
# the run directory to use (if not using DATADIR)
SARGS['RUNDIR'] = SetupArgument(name='RUNDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The run directory to use')
# the assets directory to use (if not using DATADIR)
SARGS['ASSETSDIR'] = SetupArgument(name='ASSETSDIR', default_value=None,
                                   dtype='path', required=True,
                                   depends='DATADIR',
                                   helpstr='The assets directory to use')
# the other directory to use (if not using DATADIR)
SARGS['OTHERDIR'] = SetupArgument(name='OTHERDIR', default_value=None,
                                  dtype='path', required=True,
                                  depends='DATADIR',
                                  helpstr='The other directory to use')
# whether to always create nre directories without asking user
SARGS['FORCE_DIR_CREATE'] = SetupArgument(name='FORCE_DIR_CREATE',
                                          argname='--always-create',
                                          default_value=False, dtype='bool',
                                          helpstr='Force directory creation',
                                          ask=False)
# -----------------------------------------------------------------------------
# Database settings
# -----------------------------------------------------------------------------
# which database backend to use
SARGS['DATABASE_MODE'] = SetupArgument(name='DATABASE_MODE',
                                       argname='--database-mode',
                                       default_value=__YAML__['DB_MODES'][0],
                                       dtype='str',
                                       options=__YAML__['DB_MODES'],
                                       helpstr='The database mode to use')
# the database host name
SARGS['DATABASE_HOST'] = SetupArgument(name='DATABASE_HOST',
                                       argname='--database-host',
                                       default_value='localhost',
                                       dtype='str',
                                       helpstr='The database host')
# the database user name
SARGS['DATABASE_USER'] = SetupArgument(name='DATABASE_USER',
                                       argname='--database-user',
                                       default_value='root',
                                       dtype='str',
                                       helpstr='The database user')
# the database password
SARGS['DATABASE_PASS'] = SetupArgument(name='DATABASE_PASS',
                                       argname='--database-pass',
                                       default_value='None',
                                       dtype='str',
                                       helpstr='The database password')
# the database name
SARGS['DATABASE_NAME'] = SetupArgument(name='DATABASE_NAME',
                                       argname='--database-name',
                                       default_value='None',
                                       dtype='str',
                                       helpstr='The database name')
# the sets dictionary for edit_dbtables
edt_sets = dict()
edt_sets['CALIB_DBTABLE'] = 'calib_{name}_db'
edt_sets['TELLU_DBTABLE'] = 'tellu_{name}_db'
edt_sets['FINDEX_DBTABLE'] = 'findex_{name}_db'
edt_sets['ASTROM_DBTABLE'] = 'astrom_{name}_db'
edt_sets['REJECT_DBTABLE'] = 'reject_{name}_db'
edt_sets['LOG_DBTABLE'] = 'log_{name}_db'

# whether to edit table names
SARGS['EDIT_DBTABLES'] = SetupArgument(name='EDIT_DBTABLES',
                                       argname='--edit-table-names',
                                       default_value=False, dtype='bool',
                                       helpstr='Edit table names',
                                       sets=edt_sets)
# calibration table name
SARGS['CALIB_DBTABLE'] = SetupArgument(name='CALIB_DBTABLE',
                                       argname='--calibtable',
                                       default_value='calib',
                                       dtype='str', depends='EDIT_DBTABLES',
                                       helpstr='The calibration table name')
# telluric table name
SARGS['TELLU_DBTABLE'] = SetupArgument(name='TELLU_DBTABLE',
                                       argname='--tellutable',
                                       default_value='tellu',
                                       dtype='str', depends='EDIT_DBTABLES',
                                       helpstr='The telluric table name')
# file index table name
SARGS['FINDEX_DBTABLE'] = SetupArgument(name='FINDEX_DBTABLE',
                                        argname='--findextable',
                                        default_value='findex',
                                        dtype='str', depends='EDIT_DBTABLES',
                                        helpstr='The file index table name')
# astrometric table name
SARGS['ASTROM_DBTABLE'] = SetupArgument(name='ASTROM_DBTABLE',
                                        argname='--astromtable',
                                        default_value='astrom',
                                        dtype='str', depends='EDIT_DBTABLES',
                                        helpstr='The astrometric table name')
# the reject table name
SARGS['REJECT_DBTABLE'] = SetupArgument(name='REJECT_DBTABLE',
                                        argname='--rejecttable',
                                        default_value='reject',
                                        dtype='str', depends='EDIT_DBTABLES',
                                        helpstr='The reject table name')
# the log table name
SARGS['LOG_DBTABLE'] = SetupArgument(name='LOG_DBTABLE',
                                     argname='--logtable',
                                     default_value='log',
                                     dtype='str', depends='EDIT_DBTABLES',
                                     helpstr='The log table name')
# -----------------------------------------------------------------------------
# Other settings
# -----------------------------------------------------------------------------
# set the plot mode
SARGS['PLOT_MODE'] = SetupArgument(name='PLOT_MODE', argname='--plotmode',
                                   default_value=0, dtype='str',
                                   options=__YAML__['PLOT_MODES'],
                                   helpstr='The plot mode to use')
# whether to start from a clean state
SARGS['CLEAN_START'] = SetupArgument(name='CLEAN_START', argname='--clean',
                                     default_value=True, dtype='bool',
                                     helpstr='Start from a clean state')
# whether to ptompt user a warning when clean start is True
SARGS['CLEAN_PROMPT'] = SetupArgument(name='CLEAN_PROMPT',
                                      argname='--clean-prompt',
                                      default_value=True, dtype='bool',
                                      ask=False,
                                      helpstr='Prompt user before cleaning')

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

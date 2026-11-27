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
import shlex
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from aperocore.base import base
from aperocore.base import resources
from aperocore import drs_lang
from aperocore.core import drs_misc
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from aperocore.core import drs_text


# =============================================================================
# Define variables
# =============================================================================
__PATH__ = Path(__file__).parent.parent.parent
__NAME__ = 'apero.setup.drs_setup.py'
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)
# =============================================================================
# Get variables from info.yaml
# =============================================================================
__version__ = base.__version__
__date__ = base.__date__
__authors__ = __YAML__['DRS.AUTHORS']
__release__ = __YAML__['DRS.RELEASE']
INSTRUMENTS = __YAML__['DRS.INSTRUMENTS']
# -----------------------------------------------------------------------------
# get print colours
COLOR = drs_misc.Colors()
# get ParamDict
ParamDict = param_functions.ParamDict
# Get exceptions
AperoCodedException = drs_log.AperoCodedException
# get WLOG
WLOG = drs_log.wlog
# get textwrap
textentry = drs_lang.textentry
# get the user input function
user_input = drs_text.user_input
# -----------------------------------------------------------------------------
# profiles file
PROFILE_FILE = os.path.expanduser('~/.apero/profiles.ini')
# setup files
SETUP_PATH = __PATH__.joinpath('tools', 'resources', 'setup')
# define setup files
SETUP_FILES = dict()
SETUP_FILES['setup.sh'] = 'apero_bash.sh'
SETUP_FILES['setup.bat'] = 'apero_win.bat'
# allowed methods to link external raw files into the raw directory
EXTERNAL_RAW_TYPES = ['symlink', 'hardlink']
# Choices not recoverable from the regular profile configuration.
SETUP_STATE_KEYS = ('NAME', 'FORCE_DIR_CREATE', 'EDIT_DBTABLES', 'CLEAN_START',
                    'CLEAN_PROMPT', 'DISABLE_DEMO_PROMPT')
# Gui launch options: never part of a replayed install_script.sh.
GUI_KEYS = ('GUI', 'GUI_PORT', 'GUI_HOST', 'GUI_HEADLESS')
# Environment variable a caller (the setup gui) can use to pass the
#   database password without putting it on the command line.
DATABASE_PASS_ENV = 'APERO_SETUP_DATABASE_PASS'


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
            kwargs['nargs'] = '?'
            kwargs['const'] = True
            kwargs['type'] = drs_text.true_text
            return kwargs
        else:
            kwargs['action'] = 'store'
        # ---------------------------------------------------------------------
        # deal with type
        if self.dtype is not None and 'type' not in kwargs:
            # get type translator
            typetrans = dict(zip(base.SIMPLE_STYPES, base.SIMPLE_TYPES))
            # deal with having type
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

    def print_arg(self, value: Any = None) -> Optional[str]:
        """Format a shell-safe command-line option.

        :param value: Option value, or None to omit the option.
        :return: Quoted option token, or None for an omitted value.
        """
        if value is None:
            return None
        return shlex.quote(f'{self.argname}={value}')


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
        # ---------------------------------------------------------------------
        # if command line argument is None we use the default value
        if value is None:
            params.set(arg.name, arg.default_value, source='default')
        # if value is different from default source is the command line
        else:
            if arg.restricted_chars:
                for char in arg.restricted_chars:
                    if char in value:
                        # print error message
                        eargs = [char, argname]
                        # error: Restricted character "{0}" in argument={1}
                        raise drs_log.AperoCodedException(None, '00-510-00007')
            if arg.argname in remaining:
                params.set(arg.name, value, source='default')
            else:
                params.set(arg.name, value, source='command_line')
        # keep track of processed argnames
        used.append(arg.name)
        # deal with set
        if params.sources[arg.name] == 'command_line' and arg.sets is not None:
            # loop around sets
            for key in arg.sets:
                # Explicit child options take priority over aggregate defaults.
                if raw_params.get(key) is not None:
                    continue
                # get the value
                value = arg.sets[key].format(**params)
                # update value in params
                params.set(key, value, source=f'set[{arg.name}]')
                # keep track of processed argnames
                used.append(key)
    # -------------------------------------------------------------------------
    # a password from the environment counts as given on the command line
    #   (keeps it out of process listings and logs)
    if raw_params.get('DATABASE_PASS') is None and DATABASE_PASS_ENV in (
            os.environ):
        params.set('DATABASE_PASS', os.environ[DATABASE_PASS_ENV],
                   source='command_line')
    # -------------------------------------------------------------------------
    # specific arguments
    if not params['INSTALL_SH']:
        params = fix_config_path(params)
    # return params
    return params


def ask_user(params: ParamDict, sargs: Dict[str, SetupArgument]) -> ParamDict:
    # -------------------------------------------------------------------------
    # print progress
    # log: Setup parameters
    WLOG(None, 'info', textentry('40-510-00027'))
    # loop around all arguments
    for argname in sargs:
        # get this argument
        arg = sargs[argname]
        # ---------------------------------------------------------------------
        # if we don't need to ask for this argument then continue
        if not arg.ask:
            continue
        # A replay can specify every directory without an umbrella DATADIR.
        if arg.sets and all(params.sources.get(key) == 'command_line'
                            for key in arg.sets):
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
            margs = [arg.argname, value, argname.upper()]
            # log: {0}="{1}" from command line [{2}]
            WLOG(None, '', textentry('40-510-00032', args=margs),
                 colour='magenta', wrap=False)
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
        # construct arg string name (name and cmd arg)
        argstr = f'{argname.upper()}'
        if arg.argname is not None:
            argstr += f', {arg.argname}'
        # ---------------------------------------------------------------------
        # construct the question for the user
        if arg.question_string is not None:
            qargs = [arg.question_string, argstr]
            question = '{0} [{1}]'.format(*qargs)
        else:
            # get the help string
            qhelpstr = arg.helpstr.lower()
            # deal with starting with "the"
            if qhelpstr.startswith('the'):
                qargs = [qhelpstr, argstr]
                question = 'Define {0} [{1}]'.format(*qargs)
            # deal with starting with "set"
            elif qhelpstr.startswith('set'):
                qhelpstr = qhelpstr[3:]
                qargs = [qhelpstr, argstr]
                question = 'Set {0} [{1}]'.format(*qargs)
            # deal with starting with "edit"
            elif qhelpstr.startswith('edit'):
                qhelpstr = qhelpstr[4:]
                qargs = [qhelpstr, argstr]
                question = 'Edit {0} [{1}]'.format(*qargs)
            # deal with all other cases
            else:
                qargs = [qhelpstr, argstr]
                question = 'Define the {0} [{1}]'.format(*qargs)
        # ---------------------------------------------------------------------
        # make sure the questions starts with a new line
        if not question.startswith('\n'):
            question = '\n' + question
        # ---------------------------------------------------------------------
        # get the user input
        uinput = user_input(question, dtype=dtype.lower(),
                            default=value, color='magenta',
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
    # external raw directory (conditional questions)
    params = ask_external_raw(params)
    # -------------------------------------------------------------------------
    # specific arguments
    params = fix_config_path(params)
    # -------------------------------------------------------------------------
    return params


def ask_external_raw(params: ParamDict) -> ParamDict:
    """
    Ask whether to use an external raw directory, which directory to use
    (must exist) and how to link its files into the raw directory.
    Command line values are used instead of asking where given.

    :param params: ParamDict, the setup parameters

    :return: ParamDict, the updated setup parameters (USE_EXTERNAL_RAW,
             EXTERNAL_RAW, EXTERNAL_RAW_TYPE)
    """
    # get the sources (command line values are not asked again)
    use_cmd = params.sources['USE_EXTERNAL_RAW'] == 'command_line'
    path_cmd = params.sources['EXTERNAL_RAW'] == 'command_line'
    type_cmd = params.sources['EXTERNAL_RAW_TYPE'] == 'command_line'
    # -------------------------------------------------------------------------
    # 1. do we want to use an external raw directory
    # -------------------------------------------------------------------------
    # an external raw path on the command line implies we use it
    if path_cmd:
        use_external = True
    elif use_cmd:
        use_external = bool(params['USE_EXTERNAL_RAW'])
    else:
        question = textentry('40-510-00043')
        use_external = user_input(question, dtype='YN', color='magenta')
    # deal with not using an external raw directory
    if not use_external:
        params.set('USE_EXTERNAL_RAW', False, source='user_input')
        params.set('EXTERNAL_RAW', None, source='user_input')
        return params
    params.set('USE_EXTERNAL_RAW', True, source='user_input')
    # -------------------------------------------------------------------------
    # 2. the external raw directory (must already exist)
    # -------------------------------------------------------------------------
    if path_cmd:
        external_raw = os.path.expanduser(str(params['EXTERNAL_RAW']))
        # we never create the external directory
        if not os.path.isdir(external_raw):
            raise AperoCodedException(None, '00-510-00008',
                                      targs=[external_raw])
    else:
        question = textentry('40-510-00044')
        while True:
            uinput = user_input(question, dtype='str', color='magenta')
            # a blank answer disables the external raw directory
            if uinput in ['', 'None']:
                params.set('USE_EXTERNAL_RAW', False, source='user_input')
                params.set('EXTERNAL_RAW', None, source='user_input')
                return params
            external_raw = os.path.expanduser(uinput)
            if os.path.isdir(external_raw):
                break
            WLOG(None, 'warning', textentry('40-510-00045',
                                            args=[external_raw]))
    # store as an absolute path string (links point at this path)
    external_raw = os.path.abspath(external_raw)
    params.set('EXTERNAL_RAW', external_raw, source='user_input')
    # -------------------------------------------------------------------------
    # 3. how to link the files
    # -------------------------------------------------------------------------
    if not type_cmd:
        question = textentry('40-510-00046')
        link_type = user_input(question, dtype='str', color='magenta',
                               options=EXTERNAL_RAW_TYPES,
                               default=params['EXTERNAL_RAW_TYPE'])
        params.set('EXTERNAL_RAW_TYPE', str(link_type).lower(),
                   source='user_input')
    # -------------------------------------------------------------------------
    return params


def update_setup(setup_params: ParamDict,
                 sargs: Dict[str, SetupArgument]) -> ParamDict:
    """Recover setup choices from the selected profile.

    :param setup_params: Parsed setup arguments selecting the profile.
    :param sargs: Setup argument definitions and configuration mappings.
    :return: Setup parameters populated from the installed profile.
    :raises AperoCodedException: If no profile can be selected.
    """
    # An explicit config path takes priority over an activated profile.
    cond1 = bool(os.environ.get(base.USER_ENV))
    cond2 = setup_params['NAME'] is not None
    cond3 = setup_params['CONFIG_PATH'] is not None
    # ----------------------------------------------------------------------
    # Get the config path
    # ----------------------------------------------------------------------
    if (not cond1) and not cond3:
        raise drs_log.AperoCodedException(None, '00-510-00003')
    elif not cond3:
        # get the config path
        config_path = os.environ[base.USER_ENV]
    else:
        # get the config path
        config_path = setup_params['CONFIG_PATH']
        if cond2:
            config_path = Path(config_path)
            if config_path.name != setup_params['NAME']:
                config_path = config_path / setup_params['NAME']
    config_path = Path(config_path).expanduser().resolve()
    os.environ[base.USER_ENV] = str(config_path)
    setup_params.set('CONFIG_PATH', config_path, source='profile')
    # ----------------------------------------------------------------------
    # Once DRS_UCONFIG is set we can load the parameters
    # ----------------------------------------------------------------------
    from apero.instruments import select
    # get the current install parameters
    iparams = base.load_yaml(os.path.join(config_path, 'install.yaml'))
    # Avoid a cached configuration from another profile of the same instrument.
    aparams = load_functions.load_config(select.INSTRUMENTS,
                                        iparams['OBS.INSTRUMENT'], cache=False)
    # get the current database parameters
    dparams = base.load_yaml(os.path.join(config_path, 'database.yaml'))
    # access dparams using paths
    dparam2path = param_functions.base_class.Path2Dict(dparams)
    setup_params.set('NAME', config_path.name, source='profile')
    for key in SETUP_STATE_KEYS:
        if key in iparams.get('SETUP_ARGUMENTS', {}):
            setup_params.set(key, iparams['SETUP_ARGUMENTS'][key],
                             source='apero.iparams')
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
            margs = [apero_name, value, argname.upper()]
            # log: {0}="{1}" from apero params [{2}]
            WLOG(None, '', textentry('40-510-00033', args=margs),
                 colour='magenta')
        # if the key is in the install parameters we update the setup parameters
        if install_name is not None and install_name in iparams:
            value = iparams[install_name]
            setup_params.set(argname, value, source='apero.iparams')
            margs = [install_name, value, argname.upper()]
            # log: {0}="{1}" from install params [{2}]
            WLOG(None, '', textentry('40-510-00036', args=margs),
                 colour='magenta')
        # if the key is in the database parameters we update the setup parameters
        if database_name is not None and database_name in dparam2path:
            # get value from a path
            value = dparam2path[database_name]
            setup_params.set(argname, value, source='apero.dparams')
            display_value = '********' if argname == 'DATABASE_PASS' else value
            margs = [database_name, display_value, argname.upper()]
            # log: {0}="{1}" from database params [{2}]
            WLOG(None, '', textentry('40-510-00037', args=margs),
                 colour='magenta')
    # -------------------------------------------------------------------------
    setup_params.set('USE_EXTERNAL_RAW',
                     setup_params['EXTERNAL_RAW'] not in [None, '', 'None'],
                     source='profile')
    # return the updated setup parameters
    return setup_params


def run_setup(params: ParamDict, sargs: Dict[str, SetupArgument]):
    """
    Run the setup (create files in DRS_UCONFIG)

    Files created:
    - install.yaml
    - database.yaml
    - user_config.yaml
    - user_constants.yaml
    - setup.sh
    - setup.bat
    - install_script.sh
    """
    # Create the config directory before requiring it for YAML generation.
    create_paths(params, sargs)
    os.environ[base.USER_ENV] = str(params['CONFIG_PATH'])
    # -------------------------------------------------------------------------
    # fix constants to use their apero name if they have one
    for argname in sargs:
        if sargs[argname].apero_name is not None:
            params[sargs[argname].apero_name] = params[argname]
    # -------------------------------------------------------------------------
    # create the database.yaml and install.yaml
    # log: Creating database.yaml and install.yaml
    WLOG(None, 'info', textentry('40-510-00028'))
    create_yamls(params)
    # -------------------------------------------------------------------------
    # create the user_config.yaml and user_constants.yaml
    # log: Creating user yamls
    WLOG(None, 'info', textentry('40-510-00029'))
    create_user_configs(params, sargs)
    # -------------------------------------------------------------------------
    # create the setup file (setup.sh, setup.bat)
    # log: Creating setup.sh and setup.bat
    WLOG(None, 'info', textentry('40-510-00030'))
    create_setup_files(params)
    # -------------------------------------------------------------------------
    # create an install_script.sh to reproduce the installation
    # log: Creating install_script.sh
    WLOG(None, 'info', textentry('40-510-00031'))
    create_install_script(params, sargs)
    # ----------------------------------------------------------------------
    # Now we can use apero
    # ----------------------------------------------------------------------
    from apero.tools.module.setup import drs_assets
    from apero.instruments import select
    # reload base dparams and iparams
    base.DPARAMS = base.load_database_yaml()
    base.IPARAMS = base.load_install_yaml()
    # get apero parameters
    aparams = load_functions.load_config(select.INSTRUMENTS, cache=False)

    # ----------------------------------------------------------------------
    # download the assets (into github directory)
    # ----------------------------------------------------------------------
    # log: Updating APERO assets
    WLOG(None, 'info', textentry('40-521-00007'))
    # now check whether we need to download the assets
    update_assets = drs_assets.check_local_assets(aparams)
    if update_assets:
        drs_assets.update_local_assets(aparams,
                                       tarfile=params.get('TARFILE', None))
    # ----------------------------------------------------------------------
    # clean install
    # ----------------------------------------------------------------------
    clean_install(params)

    # ----------------------------------------------------------------------
    # Populate the raw directory
    # ----------------------------------------------------------------------
    from apero.tools.module.processing import drs_processing
    drs_processing.sync_external_raw(aparams)

    # ----------------------------------------------------------------------
    # print out instructions on what to do next
    # ----------------------------------------------------------------------
    margs = [params['NAME']]
    # log: Installation complete. \n \n To launch any apero recipe you must
    #     activate your APERO profile \n \n To do this type the follow (or add
    #     to your aliases): \n \n For Linux/Mac: \n source apero_profile.sh {0}
    #     \n \n For Windows: \n aprero_profile.bat {0} \n \n To see all
    #     available apero profiles currently installed: \n \n For Linux/Mac: \n
    #     source apero_profile.sh \n \n For Windows: \n aprero_profile.bat
    WLOG(params, 'info', textentry('40-510-00042', args=margs),
         colour='magenta')


# =============================================================================
# Define other functions
# =============================================================================
def display_title():
    """
    Print the title of the script
    """
    global PROG_START
    # set clock running
    PROG_START = time.time()
    # set function name
    # _ = display_func('_display_drs_title', __NAME__)
    # get colours
    colors = COLOR
    # create title
    title = colors.okgreen + '* '
    title += colors.RED1 + ' {0} ' + colors.okgreen + '@{1}'
    title += ' (' + colors.BLUE1 + 'V{2}' + colors.okgreen + ')'
    title = title.format('APERO', 'Setup', __version__)
    title += colors.ENDC
    # header
    drs_header = '*' * base.__YAML__['LOG']['CHAR_LEN']
    # set function name
    # _ = display_func('_display_title', __NAME__)
    # print and log
    WLOG(None, '', drs_header, wrap=False)
    # add title
    WLOG(None, '', '*\n{0}\n*'.format(title), wrap=False)
    # end header
    WLOG(None, '', drs_header, wrap=False)
    # print logo
    for line in resources.apero_logo():
        WLOG(None, '', colors.RED1 + line + colors.ENDC, wrap=False,
             printonly=True)
    # print and log
    WLOG(None, '', drs_header)


def end_all(params: Optional[ParamDict],
            recipename: str = 'apero_setup.py') -> None:
    """
    Quick end script
    """
    if params is None:
        params = drs_log.MPARAMS
    # get the time now
    duration = time.time() - PROG_START
    # log the success
    iargs = [str(params.get('RECIPE', recipename))]
    WLOG(params, 'info', params['LOG.HEADER'])
    # text: Recipe {0} has been successfully completed
    msg = textentry('40-003-00001', args=iargs)
    if duration is not None:
        msg += f'\t({duration:.3f} seconds)'
    WLOG(params, 'info', msg)
    WLOG(params, 'info', params['LOG.HEADER'])


def fix_config_path(params: ParamDict) -> ParamDict:
    """
    Fix the config path (make sure it ends with the name)

    :param params: ParamDict, the parameters to fix

    :return params: ParamDict, the fixed parameters
    """
    # only do this if we have both the name and config_path
    if params['NAME'] is not None and params['CONFIG_PATH'] is not None:
        # force config path to a Path object
        if isinstance(params['CONFIG_PATH'], str):
            params['CONFIG_PATH'] = Path(params['CONFIG_PATH'])
        # make sure config_path ends with the name
        if not str(params['CONFIG_PATH']).endswith(params['NAME']):
            # add the name to the end of the config_path
            config_path = params['CONFIG_PATH'].joinpath(params['NAME'])
            # update parmaeters
            params.set('CONFIG_PATH', config_path, source='command_line')
            # need to make sure this exists
            os.makedirs(config_path, exist_ok=True)
    # return parameters (updated or not)
    return params


def create_paths(params: ParamDict,
                 sargs: Dict[str, SetupArgument]) -> None:
    """Validate configured paths and create any missing directories.

    :param params: Setup parameters containing resolved path values.
    :param sargs: Argument definitions used to identify path settings.
    :return: None. Creates missing directories or raises on failure.
    """
    # -------------------------------------------------------------------------
    # print progress
    # log: Validating paths
    WLOG(None, 'info', textentry('40-510-00001'))
    # -------------------------------------------------------------------------
    created = False
    # loop around all variables and look for paths
    for sname in sargs:
        # get the setup argument
        sarg = sargs[sname]
        # if we have a path try to create it if it doesn't exist
        if sarg.dtype == 'path':
            if params[sname] is None and not sarg.required:
                continue
            try:
                # get the path
                path = Path(params[sname])
                # check if path exists
                if not path.exists():
                    # print progress
                    margs = [sname, path]
                    # log: Creating path {0}: {1}
                    WLOG(None, '', textentry('40-510-00023', args=margs))
                    # create path
                    path.mkdir(parents=True, exist_ok=True)
                    # set created to True
                    created = True
                if not path.is_dir():
                    raise NotADirectoryError(str(path))
            except Exception as e:
                # print error message
                eargs = [params[sname], type(e), str(e)]
                # error: Error creating path: {0} \n {1}: {2}
                raise drs_log.AperoCodedException(None, '00-510-00006',
                                                  targs=eargs)
    # -------------------------------------------------------------------------
    # deal with no paths created
    if not created:
        # log: No paths created
        WLOG(None, '', textentry('40-510-00004'))


def create_yamls(params: ParamDict) -> None:
    """
    Create the yaml files from allparams

    :param allparams: ParamDict, the parameter dictionary of installation

    :return: None - writes install.yaml and database.yaml
    """
    # get config directory
    userconfig = Path(params['CONFIG_PATH'])
    # -------------------------------------------------------------------------
    # create install yaml
    # -------------------------------------------------------------------------
    # get instrument
    instrument = params['OBS.INSTRUMENT'].upper()
    # get save path
    install_path = userconfig.joinpath(base.INSTALL_YAML)
    # populate dictionary
    install_dict = dict()
    install_dict[base.USER_ENV] = str(userconfig)
    install_dict['OBS.INSTRUMENT'] = instrument
    install_dict['GLOBAL.LANGUAGE'] = params['GLOBAL.LANGUAGE']
    install_dict['USE_TQDM'] = True
    install_dict['SETUP_ARGUMENTS'] = {
        key: params[key] for key in SETUP_STATE_KEYS
    }
    # -------------------------------------------------------------------------
    # add the language modules
    lang_modules = base.__YAML__['LANGUAGE_MODULES']
    # add the default modules
    install_dict['DRS_LANG_MODULES'] = lang_modules['DEFAULT']
    # add the instruments language module
    if instrument in lang_modules and instrument != 'DEFAULT':
        install_dict['DRS_LANG_MODULES'] += lang_modules[instrument]
    # -------------------------------------------------------------------------
    # print writing
    margs = [install_path]
    # log: Writing install.yaml: {0}
    WLOG(None, '', textentry('40-510-00034', args=margs), wrap=False)
    # write database
    base.write_yaml(install_dict, str(install_path))
    # -------------------------------------------------------------------------
    # create database yaml
    # -------------------------------------------------------------------------
    # get save path
    database_path = userconfig.joinpath(base.DATABASE_YAML)
    # populate dictionary
    database_dict = dict()
    # -------------------------------------------------------------------------
    #  DATABASE SETTINGS
    # -------------------------------------------------------------------------
    # add database settings
    database_dict['TYPE'] = params.get('DATABASE_MODE', 'NULL')
    database_dict['HOST'] = params.get('DATABASE_HOST', 'NULL')
    database_dict['USER'] = params.get('DATABASE_USER', 'NULL')
    database_dict['PASSWD'] = params.get('DATABASE_PASS', 'NULL')
    database_dict['DATABASE'] = params.get('DATABASE_NAME', 'NULL')
    database_dict['USE_SSL'] = params.get('DATABASE_USE_SSL', False)
    # add calib database
    calibdb = dict()
    calibdb['NAME'] = params.get('CALIB_NAME', 'calib')
    calibdb['TABLE'] = params.get('CALIB_DBTABLE', 'calib_default')
    database_dict['CALIB'] = calibdb
    # add tellu database
    telludb = dict()
    telludb['NAME'] = params.get('TELLU_NAME', 'tellu')
    telludb['TABLE'] = params.get('TELLU_DBTABLE', 'tellu_default')
    database_dict['TELLU'] = telludb
    # add index database
    findexdb = dict()
    findexdb['NAME'] = params.get('FINDEX_NAME', 'findex')
    findexdb['TABLE'] = params.get('FINDEX_DBTABLE', 'findex_default')
    database_dict['FINDEX'] = findexdb
    # add log database
    logdb = dict()
    logdb['NAME'] = params.get('LOG_NAME', 'log')
    logdb['TABLE'] = params.get('LOG_DBTABLE', 'log_default')
    database_dict['LOG'] = logdb
    # print writing
    margs = [database_path]
    # log: Writing database.yaml: {0}
    WLOG(None, '', textentry('40-510-00035', args=margs), wrap=False)
    # write database
    base.write_yaml(database_dict, str(database_path))


def create_user_configs(
    params: ParamDict, sargs: Dict[str, SetupArgument]
) -> None:
    """
    Create the user_config.yaml and user_constants.yaml files
    for the user specified instrument

    :param params: ParamDict, the parameters to use

    :return: None, writes user_config.yaml and user_constants.yaml to file
    """
    # set function name
    func_name = f'{__NAME__}.create_user_configs()'
    # get config directory
    userconfig = Path(params['CONFIG_PATH'])
    # import modules here
    from apero.instruments.default import config, constants, keywords
    from apero.instruments import select
    # -------------------------------------------------------------------------
    # get the user scripts
    user_scripts = config.CDict['DRS.USER_SCRIPTS']
    # get the modules for CDicts (config, constants)
    mod_scripts = [config, constants, keywords]
    # -------------------------------------------------------------------------
    # temporary load constants for this instrument
    apero_params = load_functions.load_config(select.INSTRUMENTS,
                                              params['OBS.INSTRUMENT'],
                                              from_file=False, check=False,
                                              cache=False)
    # -------------------------------------------------------------------------
    # push the required parameters into apero_params
    for sname in sargs:
        # get the setup argument
        sarg = sargs[sname]
        # if not defined in parameters we skip
        if sname not in params:
            continue
        # otherwise add argument to apero_params is we have an apero name
        if sarg.apero_name is not None:
            apero_params[sarg.apero_name] = params[sname]
    # -------------------------------------------------------------------------
    # get the title arguments
    tkwargs = dict(INSTRUMENT=params['OBS.INSTRUMENT'])
    # loop around user scripts and create the yamls
    for it in range(len(user_scripts)):
        # don't continue if we don't have a Cdict module defined
        if mod_scripts[it] is None:
            continue
        # construct the path
        outpath = userconfig.joinpath(user_scripts[it])
        # print writing
        margs = [user_scripts[it], outpath]
        # log: Writing {0}: {1}
        WLOG(None, '', textentry('40-510-00005', args=margs), wrap=False)
        # get the correct storage class
        if hasattr(mod_scripts[it], 'CDict'):
            SDict = mod_scripts[it].CDict
        elif hasattr(mod_scripts[it], 'KDict'):
            SDict = mod_scripts[it].KDict
        else:
            eargs = [user_scripts[it], func_name]
            # error: Mod script {0} has no CDict or KDict class func_name={1}
            raise AperoCodedException(None, '00-510-00005', targs=eargs)
        # save the yaml file
        SDict.save_yaml(apero_params, outpath=outpath, title_args=tkwargs,
                        log=False)


def create_setup_files(params: ParamDict) -> None:
    """Create the shell/profile files for the configured APERO installation.

    :param params: Setup parameters including target paths and profile name.
    :return: None. Writes configured files beneath the user config directory.
    """
    # get config directory
    userconfig = Path(params['CONFIG_PATH'])
    # setup the user config directory
    kwargs = dict()
    kwargs['ROOT_PATH'] = str(__PATH__)
    kwargs['USER_CONFIG'] = str(userconfig)
    kwargs['USER_NAME'] = params['NAME']
    kwargs['NAME'] = str(params['NAME'])
    kwargs['APERO_PROFILE'] = params['NAME']
    kwargs['DRS_PS1+x'] = '{DRS_PS1+x}'
    # -------------------------------------------------------------------------
    # loop around setup files
    for setup_file in SETUP_FILES:
        # get the source and destination
        source = SETUP_PATH.joinpath(SETUP_FILES[setup_file])
        destination = userconfig.joinpath(setup_file)
        # ----------------------------------------------------------------
        # open the source file
        with open(source, 'r') as sf:
            # read the source file as a single string
            sfile = sf.read()
        # need to push kwargs into sfile
        sfile = sfile.format(**kwargs)
        # ---------------------------------------------------------------------
        # print progress
        margs = [destination]
        # log: Writing setup file: {0}
        WLOG(None, '', textentry('40-510-00022', args=margs), wrap=False)
        # ---------------------------------------------------------------------
        # write the destination file
        with open(destination, 'w') as df:
            # write the source file to the destination file
            df.write(sfile)
        # ---------------------------------------------------------------------
        # make the file executable
        os.chmod(destination, 0o755)
    # -------------------------------------------------------------------------
    # Deal with profile.ini
    # -------------------------------------------------------------------------
    # Add a profile.ini file if it doesn't exist
    if not os.path.exists(PROFILE_FILE):
        # print progress
        margs = [PROFILE_FILE]
        # log: Creating profile.ini: {0}
        WLOG(None, '', textentry('40-510-00006', args=margs))
        # convert to dictionary
        profiles = dict()
    else:
        # print progress
        margs = [PROFILE_FILE]
        # log: Adding to profile.ini: {0}
        WLOG(None, '', textentry('40-510-00007', args=margs))
        # load the profile file
        with open(PROFILE_FILE, 'r') as afile:
            lines = afile.readlines()
        # convert to dictionary
        profiles = dict()
        for line in lines:
            if len(line.split('=')) != 2:
                continue
            key, value = line.split('=')
            profiles[key.strip()] = value.strip()
    # add or replace  the new profile
    if params['NAME'] in profiles:
        margs = [params['NAME']]
        # log: Replacing profile: {0}
        WLOG(None, '', textentry('40-510-00008', args=margs))
    # push name into profiles
    profiles[params['NAME']] = str(userconfig)
    # write to file
    with open(PROFILE_FILE, 'w') as afile:
        for key, value in profiles.items():
            afile.write('{0}={1}\n'.format(key, value))


def create_install_script(params: ParamDict,
                          sargs: Dict[str, SetupArgument]) -> None:
    """
    Create an executable install_script.sh in the profile config directory.

    :param params: ParamDict, the parameters to use
    :param sargs: dict, the setup arguments to use

    :return: None, writes install_script.sh without modifying parameters.
    :raises OSError: If the script cannot be written or made executable.
    """
    setup_script = __PATH__.joinpath('setup', 'bin', 'apero_setup.py')
    command = [shlex.quote(sys.executable), shlex.quote(str(setup_script))]
    # Mode switches must never turn a replay into an update or regeneration.
    excluded = {'UPDATE', 'INSTALL_SH', 'DATADIR'}.union(GUI_KEYS)
    for sname, sarg in sargs.items():
        if sname.upper() in excluded:
            continue
        value = params[sname]
        if sarg.dtype == 'path' and value is not None:
            value = Path(value).expanduser().resolve()
        option = sarg.print_arg(value)
        if option is not None:
            command.append(option)
    destination = Path(params['CONFIG_PATH']).joinpath('install_script.sh')
    margs = [destination]
    WLOG(None, '', textentry('40-510-00002', args=margs), wrap=False)
    # Restrict access before writing: database options can include credentials.
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o700)
    with os.fdopen(fd, 'w') as afile:
        os.fchmod(afile.fileno(), 0o700)
        afile.write('#!/bin/sh\nexec ' + ' \\\n    '.join(command) + ' "$@"\n')


def clean_install(params: ParamDict) -> None:
    """Run the requested pre-install cleanup, if enabled.

    :param params: Setup parameters controlling cleanup and prompt behavior.
    :return: None. Performs cleanup or raises when reset fails.
    """
    # clean install
    if not params['CLEAN_START']:
        return
    # -------------------------------------------------------------------------
    # print progress
    # log: Cleaning installation using apero_reset.py
    WLOG(None, 'info', textentry('40-510-00003'))
    # import apero_reset here
    from apero.tools.recipes.bin import apero_reset
    # Reset's nowarn flag has the opposite meaning to CLEAN_PROMPT.
    nowarn = not params['CLEAN_PROMPT']
    # construct reset command
    reset_args = apero_reset.main(quiet=True, nowarn=nowarn,
                                  database_timeout=0)
    # deal with a bad reset
    if not reset_args['success']:
        # error message: Error resetting database (see above) cannot install
        #                apero
        raise AperoCodedException(None, '40-001-00083')


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

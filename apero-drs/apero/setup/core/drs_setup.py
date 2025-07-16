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
__version__ = __YAML__['DRS.VERSION']
__authors__ = __YAML__['DRS.AUTHORS']
__date__ = __YAML__['DRS.DATE']
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

        # if we don't have a value set then don't add this argument
        if value is None:
            return None
        # ---------------------------------------------------------------------
        # deal with argname
        if self.argname is not None:
            argname = self.argname
        else:
            argname = self.name
        # ---------------------------------------------------------------------
        # deal with value
        value = str(value)
        # deal with white spaces
        if ' ' in value:
            value = f'"{value}"'
        # ---------------------------------------------------------------------
        # deal with command
        command = f'--{argname}={value}'
        # return command
        return command


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
                        emsg = 'Restricted character "{0}" in argument={1}'
                        eargs = [char, argname]
                        raise drs_log.AperoCodedException(None, message=emsg,
                                                          targs=eargs)
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
    # -------------------------------------------------------------------------
    # print progress
    msg = 'Setup parameters'
    WLOG(None, 'info', msg)
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
            msg = '\t{0}="{1}" from command line [{2}]'
            margs = [arg.argname, value, argname.upper()]
            WLOG(None, '', msg.format(*margs), colour='magenta', wrap=False)
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
    # specific arguments
    params = fix_config_path(params)
    # -------------------------------------------------------------------------
    return params


def update_setup(setup_params: ParamDict,
                 sargs: Dict[str, SetupArgument]) -> ParamDict:

    # if we have a environment variable we can get current parameters from
    # the setup directory
    cond1 = base.USER_ENV in os.environ
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
        config_path = os.environ[base.USER_ENV]
    else:
        # get the config path
        config_path = setup_params['CONFIG_PATH']
        # lets set this in os.envinron
        os.environ[base.USER_ENV] = config_path
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
            WLOG(None, '', msg.format(*margs), colour='magenta')
        # if the key is in the install parameters we update the setup parameters
        if install_name is not None and install_name in iparams:
            value = iparams[install_name]
            setup_params.set(argname, value, source='apero.iparams')
            msg = '{0}="{1}" from install params [{2}]'
            margs = [install_name, value, argname.upper()]
            WLOG(None, '', msg.format(*margs), colour='magenta')
        # if the key is in the database parameters we update the setup parameters
        if database_name is not None and database_name in dparam2path:
            # get value from a path
            value = dparam2path[database_name]
            setup_params.set(argname, value, source='apero.dparams')
            msg = '{0}="{1}" from database params [{2}]'
            margs = [database_name, value, argname.upper()]
            WLOG(None, '', msg.format(*margs), colour='magenta')
    # -------------------------------------------------------------------------
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
    - install.sh
    """
    # check that config path exists - we need this to continue
    if not os.path.exists(params['CONFIG_PATH']):
        emsg = 'Config path does not exist: {0}'
        eargs = [params['CONFIG_PATH']]
        raise drs_log.AperoCodedException(None, message=emsg.format(*eargs))
    else:
        os.environ[base.USER_ENV] = str(params['CONFIG_PATH'])
    # -------------------------------------------------------------------------
    # fix constants to use their apero name if they have one
    for argname in sargs:
        if sargs[argname].apero_name is not None:
            params[sargs[argname].apero_name] = params[argname]
    # -------------------------------------------------------------------------
    # check profile name in .apero
    # -------------------------------------------------------------------------
    # create paths
    create_paths(params, sargs)
    # -------------------------------------------------------------------------
    # create the database.yaml and install.yaml
    msg = 'Creating database.yaml and install.yaml'
    WLOG(None, 'info', msg)
    create_yamls(params)
    # -------------------------------------------------------------------------
    # create the user_config.yaml and user_constants.yaml
    msg = 'Creating user_config.yaml and user_constants.yaml'
    WLOG(None, 'info', msg)
    create_user_configs(params, sargs)
    # -------------------------------------------------------------------------
    # create the setup file (setup.sh, setup.bat)
    msg = 'Creating setup.sh and setup.bat'
    WLOG(None, 'info', msg)
    create_setup_files(params)
    # -------------------------------------------------------------------------
    # create an install.sh to reproduce the installation
    msg = 'Creating install.sh'
    WLOG(None, 'info', msg)
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
    msg = 'Updating APERO assets'
    WLOG(None, 'info', msg)
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
    # print out instructions on what to do next
    # ----------------------------------------------------------------------
    msg = 'Installation complete.'
    msg += '\n\n To launch any apero recipe you must activate your APERO profile'
    msg += '\n\n To do this type the follow (or add to your aliases): '
    msg += '\n\n For Linux/Mac:'
    msg += '\n\t source apero_profile.sh {0}'
    msg += '\n\n For Windows:'
    msg += '\n\t aprero_profile.bat {0}'
    msg += '\n\n To see all available apero profiles currently installed:'
    msg += '\n\n For Linux/Mac:'
    msg += '\n\t source apero_profile.sh'
    msg += '\n\n For Windows:'
    msg += '\n\t aprero_profile.bat'

    WLOG(params, 'info', msg.format(params['NAME']), colour='magenta')


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


def end_all(params, recipename='apero_setup.py'):
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
            if not os.path.exists(config_path):
                os.makedirs(config_path)
    # return parameters (updated or not)
    return params


def create_paths(params: ParamDict, sargs: Dict[str, SetupArgument]):
    # -------------------------------------------------------------------------
    # print progress
    WLOG(None, 'info', 'Validating paths')
    # -------------------------------------------------------------------------
    created = False
    # loop around all variables and look for paths
    for sname in sargs:
        # get the setup argument
        sarg = sargs[sname]
        # if we have a path try to create it if it doesn't exist
        if sarg.dtype == 'path':
            try:
                # get the path
                path = Path(params[sname])
                # check if path exists
                if not path.exists():
                    # print progress
                    msg = '\tCreating path {0}: {1}'
                    margs = [sname, path]
                    WLOG(None, '', msg.format(*margs))
                    # create path
                    path.mkdir(parents=True)
                    # set created to True
                    created = True
            except Exception as e:
                # print error message
                emsg = 'Error creating path: {0}\n\t{1}: {2}'
                eargs = [params[sname], type(e), str(e)]
                raise drs_log.AperoCodedException(None,
                                                  message=emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # deal with no paths created
    if not created:
        WLOG(None, '', '\tNo paths created')


def create_yamls(params: Any):
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
    msg = '\tWriting install.yaml: {0}'.format(install_path)
    WLOG(None, '', msg, wrap=False)
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
    calibdb['RESET'] = params.get('CALIB_RESET', 'reset.calib.csv')
    calibdb['TABLE'] = params.get('CALIB_DBTABLE', 'NULL')
    database_dict['CALIB'] = calibdb
    # add tellu database
    telludb = dict()
    telludb['NAME'] = params.get('TELLU_NAME', 'tellu')
    telludb['RESET'] = params.get('TELLU_RESET', 'reset.tellu.csv')
    telludb['TABLE'] = params.get('TELLU_DBTABLE', 'NULL')
    database_dict['TELLU'] = telludb
    # add index database
    findexdb = dict()
    findexdb['NAME'] = params.get('FINDEX_NAME', 'findex')
    findexdb['RESET'] = params.get('FINDEX_RESET', 'NULL')
    findexdb['TABLE'] = params.get('FINDEX_DBTABLE', 'NULL')
    database_dict['FINDEX'] = findexdb
    # add log database
    logdb = dict()
    logdb['NAME'] = params.get('LOG_NAME', 'log')
    logdb['RESET'] = params.get('LOG_RESET', 'NULL')
    logdb['TABLE'] = params.get('LOG_DBTABLE', 'NULL')
    database_dict['LOG'] = logdb
    # add object database
    astromdb = dict()
    astromdb['NAME'] = params.get('ASTROM_NAME', 'astrom')
    astromdb['RESET'] = params.get('ASTROM_RESET', 'reset.astrom.csv')
    astromdb['TABLE'] = params.get('ASTROM_DBTABLE', 'NULL')
    database_dict['ASTROM'] = astromdb
    # add reject database
    rejectdb = dict()
    rejectdb['NAME'] = params.get('REJECT_NAME', 'reject')
    rejectdb['RESET'] = params.get('REJECT_RESET', 'NULL')
    rejectdb['TABLE'] = params.get('REJECT_PROFILE', 'NULL')
    database_dict['REJECT'] = rejectdb
    # print writing
    msg = '\tWriting database.yaml: {0}'.format(database_path)
    WLOG(None, '', msg, wrap=False)
    # write database
    base.write_yaml(database_dict, str(database_path))


def create_user_configs(params: ParamDict, sargs: Dict[str, SetupArgument]):
    """
    Create the user_config.yaml and user_constants.yaml files
    for the user specified instrument

    :param params: ParamDict, the parameters to use

    :return: None, writes user_config.yaml and user_constants.yaml to file
    """
    # get config directory
    userconfig = Path(params['CONFIG_PATH'])
    # import modules here
    from apero.instruments.default import config, constants
    from apero.instruments import select
    # -------------------------------------------------------------------------
    # get the user scripts
    user_scripts = config.CDict['DRS.USER_SCRIPTS']
    # get the modules for CDicts (config, constants)
    mod_scripts = [config, constants, None]
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
        WLOG(None, '', '\tWriting {0}: {1}'.format(user_scripts[it], outpath),
             wrap=False)
        # save the yaml file
        mod_scripts[it].CDict.save_yaml(apero_params, outpath=outpath,
                                        title_args=tkwargs, log=False)


def create_setup_files(params: ParamDict):
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
        msg = '\tWriting setup file: {0}'
        margs = [destination]
        WLOG(None, '', msg.format(*margs), wrap=False)
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
        WLOG(None, '', '\tCreating profile.ini: {0}'.format(PROFILE_FILE))
        # convert to dictionary
        profiles = dict()
    else:
        # print progress
        WLOG(None, '', '\tAdding to profile.ini: {0}'.format(PROFILE_FILE))
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
        WLOG(None, '', '\tReplacing profile: {0}'.format(params['NAME']))
    # push name into profiles
    profiles[params['NAME']] = str(userconfig)
    # write to file
    with open(PROFILE_FILE, 'w') as afile:
        for key, value in profiles.items():
            afile.write('{0}={1}\n'.format(key, value))


def create_install_script(params: ParamDict, sargs: Dict[str, SetupArgument]):
    """
    Create the install.sh script to reproduce the installation

    :param params: ParamDict, the parameters to use
    :param sargs: dict, the setup arguments to use

    :return: None, writes install.sh to file
    """
    # write command
    command = f'python apero_setup.py          \\'
    # -------------------------------------------------------------------------
    # set always create to true (even if False)
    params['FORCE_DIR_CREATE'] = True
    # -------------------------------------------------------------------------
    # remove profile name from config path (for arguments)
    #   but keep config_path for saving file to
    config_path = str(params['CONFIG_PATH'])
    if str(config_path).endswith(params['NAME']):
        config_path = str(config_path)[:-len(params['NAME'])]
    params['CONFIG_PATH'] = config_path
    # -------------------------------------------------------------------------
    # add non null arguments
    for it, sname in enumerate(sargs):
        # get the argument
        sarg = sargs[sname]
        # only add arguments which are not still None
        if params[sname] is not None:
            # set up command prefix
            prefix = '\n' + 10 * ' '
            # -----------------------------------------------------------------
            # set up command suffix (different for last argument)
            if it != len(sargs) - 1:
                suffix = ' ' * 4 + '\\'
            else:
                suffix = ''
            # -----------------------------------------------------------------
            # add command
            command += prefix + sarg.print_arg(params[sname]) + suffix
    # construct path
    destination = os.path.join(config_path, 'install.sh')
    # print writing
    WLOG(None, '', '\tWriting install.sh: {0}'.format(destination), wrap=False)
    # write to file
    with open(destination, 'w') as afile:
        afile.write(command)
    # ---------------------------------------------------------------------
    # make the file executable
    os.chmod(destination, 0o755)


def clean_install(params: ParamDict):
    # clean install
    if not params['CLEAN_START']:
        return
    # -------------------------------------------------------------------------
    # print progress
    WLOG(None, 'info', 'Cleaning installation using apero_reset.py')
    # import apero_reset here
    from apero.tools.recipes.bin import apero_reset
    # define clean warn
    cleanwarn = params['CLEAN_PROMPT']
    # construct reset command
    reset_args = apero_reset.main(quiet=True, nowarn=cleanwarn,
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

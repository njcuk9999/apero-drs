#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO setup gui: command builders, setup choices and profiles

Builds the commands the gui runs from the browser forms:

    - apero_setup.py (new profile, from the Setup tab)
    - apero_setup.py --update (re-run setup of a profile, Edit tab)
    - apero_setup.py --install_sh (regenerate install_script.sh)
    - apero_validate.py [--reportfile] (Validate tab)

Every builder returns both the command that is executed and the "CLI
equivalent" a user could type, so the two never drift apart. The setup form
uses the setup argument definitions (setup_constants.SARGS) directly, so
the gui asks exactly the questions apero_setup.py asks in the terminal.

The database password is never put on a command line: it is passed in the
APERO_SETUP_DATABASE_PASS environment variable (see drs_setup).

Created on 2026-11-27

@author: cook
"""
import importlib.metadata as importlib_metadata
import os
import shlex
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from aperocore import drs_lang
from aperocore.base import base

from apero.setup.core import drs_setup
from apero.setup.core import setup_constants

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.setup.gui.commands.py'
# get the text entry function
textentry = drs_lang.textentry
# the setup argument definitions
SARGS = setup_constants.SARGS
# the apero package directory (.../apero)
APERO_DIR = Path(__file__).resolve().parents[2]
# the scripts the gui runs
SETUP_SCRIPT = APERO_DIR.joinpath('setup', 'bin', 'apero_setup.py')
VALIDATE_SCRIPT = APERO_DIR.joinpath('tools', 'recipes', 'bin',
                                     'apero_validate.py')
RESET_SCRIPT = APERO_DIR.joinpath('tools', 'recipes', 'bin',
                                  'apero_reset.py')
# the profile registry written by apero_setup
PROFILE_FILE = drs_setup.PROFILE_FILE
# arguments the setup form never sets (modes, gui options, automatic)
#   (compared in upper case: some setup argument names are lower case)
SKIP_ARGS = ['UPDATE', 'INSTALL_SH', 'APERO_PATH',
             'DATABASE_PASS'] + list(drs_setup.GUI_KEYS)
# the data directory arguments (set together by DATADIR)
DIR_ARGS = list(SARGS['DATADIR'].sets.keys())
# the table name arguments (set together by EDIT_DBTABLES)
TABLE_ARGS = list(SARGS['EDIT_DBTABLES'].sets.keys())
# the external raw arguments (only used with USE_EXTERNAL_RAW)
EXTERNAL_ARGS = ['EXTERNAL_RAW', 'EXTERNAL_RAW_TYPE']
# short descriptions of the instruments (setup cards)
INSTRUMENT_DESCS = dict(SPIROU='SPIRou (CFHT) near-infrared '
                               'spectropolarimeter',
                        NIRPS_HA='NIRPS (ESO 3.6m) high accuracy mode',
                        NIRPS_HE='NIRPS (ESO 3.6m) high efficiency mode')
# the files of a profile the Edit tab can open (name -> editable)
CONFIG_FILES = dict([('install.yaml', True), ('database.yaml', True),
                     ('user_config.yaml', True),
                     ('user_constants.yaml', True),
                     ('user_keywords.yaml', True), ('setup.sh', False),
                     ('setup.bat', False), ('install_script.sh', False)])
# the constants file of each user yaml (for the Docs links)
USER_YAMLS = ['user_config.yaml', 'user_constants.yaml',
              'user_keywords.yaml']
# shown instead of the database password
MASK = '********'
# the files setup writes that must exist before a reset / data browsing
SETUP_FILES = ['install.yaml', 'user_config.yaml', 'database.yaml']
# the data directories of a profile (Data tab): (user_config key, label,
#   setup argument with the description, protected = never deleted from)
DATA_DIRS = [('PATH.RAW', 'raw', 'RAWDIR', True),
             ('PATH.PP', 'tmp', 'TMPDIR', False),
             ('PATH.RED', 'red', 'REDDIR', False),
             ('PATH.CALIB', 'calib', 'CALDIR', False),
             ('PATH.TELLU', 'tellu', 'TELDIR', False),
             ('PATH.OUT', 'out', 'OUTDIR', False),
             ('PATH.LBL', 'lbl', 'LBLDIR', False),
             ('PATH.ASSETS', 'assets', 'ASSETSDIR', False),
             ('PATH.LOG', 'log', 'LOGDIR', False),
             ('PATH.PLOT', 'plot', 'PLOTDIR', False),
             ('PATH.RUN', 'run', 'RUNDIR', False),
             ('PATH.OTHER', 'other', 'OTHERDIR', False),
             ('PATH.EXTERNAL_RAW', 'external raw', 'EXTERNAL_RAW', True)]
# the parts apero_reset.py can reset (--only_{name}) and their directory
RESET_PARTS = [('assets', 'PATH.ASSETS'), ('tmp', 'PATH.PP'),
               ('red', 'PATH.RED'), ('calib', 'PATH.CALIB'),
               ('tellu', 'PATH.TELLU'), ('log', 'PATH.LOG'),
               ('plot', 'PATH.PLOT'), ('run', 'PATH.RUN'),
               ('lbl', 'PATH.LBL'), ('out', 'PATH.OUT'),
               ('other', 'PATH.OTHER'), ('queue', None)]
# the longest a directory size count may take (seconds)
STATS_SECONDS = 8.0


# =============================================================================
# Define classes
# =============================================================================
class CommandError(ValueError):
    """Raised when a gui form cannot be turned into a valid command"""


# =============================================================================
# Define choice functions
# =============================================================================
def _arg_info(sarg: Any) -> Dict[str, Any]:
    """
    Describe one setup argument for the browser (json friendly)

    :param sarg: SetupArgument, the setup argument

    :return: dict(name, argname, default, dtype, help, options, optiondescs,
             required, depends, sets, ask, apero_name, database_name)
    """
    default = sarg.default_value
    return dict(name=sarg.name, argname=sarg.argname,
                default=None if default is None else (
                    default if isinstance(default, (bool, int, float))
                    else str(default)),
                dtype=str(sarg.dtype), help=str(sarg.helpstr),
                options=None if sarg.options is None else [
                    str(opt) for opt in sarg.options],
                optiondescs=sarg.optiondescs, required=sarg.required,
                depends=sarg.depends, sets=sarg.sets, ask=sarg.ask,
                restricted=restricted_chars(sarg),
                apero_name=sarg.apero_name,
                database_name=sarg.database_name)


def restricted_chars(sarg: Any) -> List[str]:
    """
    Get the single characters a setup argument may not contain

    setup_constants.EXC_CHARS splits string.punctuation on the space that
    replaced "_", giving two long strings rather than characters; the gui
    checks each character (and white space) on its own

    :param sarg: SetupArgument, the setup argument

    :return: list of str, the characters (empty if unrestricted)
    """
    if not sarg.restricted_chars:
        return []
    chars = sorted(set(''.join(sarg.restricted_chars)))
    return chars + [' ']


def apero_version() -> str:
    """
    Get the installed APERO version (without importing apero.base, which
    needs an activated profile)

    :return: str, the version (apero-core version if apero is not
             installed as a distribution)
    """
    try:
        return importlib_metadata.version('apero')
    except importlib_metadata.PackageNotFoundError:
        return str(drs_setup.__version__)


def setup_choices() -> Dict[str, Any]:
    """
    Get everything the setup form needs (argument definitions, instruments,
    database / plot modes, languages, profiles)

    :return: dict, json friendly choices
    """
    instruments = [dict(name=str(inst),
                        desc=INSTRUMENT_DESCS.get(str(inst), ''))
                   for inst in setup_constants.INSTRUMENTS
                   if str(inst).upper() != 'NONE']
    plot_modes = [dict(value=int(mode), desc=str(desc)) for mode, desc
                  in zip(setup_constants.PLOT_MODES,
                         setup_constants.PLOT_DESCS)]
    return dict(args={name: _arg_info(sarg) for name, sarg in SARGS.items()},
                order=list(SARGS.keys()), instruments=instruments,
                db_modes=[str(mode) for mode in setup_constants.DB_MODES],
                plot_modes=plot_modes,
                languages=[str(lang) for lang in base.LANGUAGES],
                default_language=str(base.DEFAULT_LANG),
                external_types=list(setup_constants.EXTERNAL_RAW_TYPES),
                dir_args=DIR_ARGS, table_args=TABLE_ARGS,
                profiles=list_profiles(), pass_env=drs_setup.DATABASE_PASS_ENV,
                version=apero_version())


# =============================================================================
# Define profile functions
# =============================================================================
def read_profiles() -> Dict[str, str]:
    """
    Read ~/.apero/profiles.ini (profile name -> DRS_UCONFIG directory)

    :return: dict, name -> directory (in file order)
    """
    profiles: Dict[str, str] = dict()
    if not os.path.isfile(PROFILE_FILE):
        return profiles
    with open(PROFILE_FILE, 'r', encoding='utf-8') as pfile:
        for line in pfile:
            # lines are name=path (anything else is ignored, as in setup)
            if len(line.split('=')) != 2:
                continue
            key, value = line.split('=')
            profiles[key.strip()] = value.strip()
    return profiles


def profile_info(path: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Describe one profile directory (DRS_UCONFIG)

    :param path: str, the profile directory
    :param name: str or None, the registered name (default: directory name)

    :return: dict(name, path, exists, valid, instrument, language, mtime,
             files)
    """
    path = os.path.realpath(os.path.expanduser(str(path)))
    info: Dict[str, Any] = dict(name=name or os.path.basename(path),
                                path=path, exists=os.path.isdir(path))
    install_path = os.path.join(path, base.INSTALL_YAML)
    info['valid'] = os.path.isfile(install_path)
    if info['valid']:
        try:
            with open(install_path, 'r', encoding='utf-8') as ifile:
                install = yaml.safe_load(ifile) or dict()
            info['instrument'] = install.get('OBS.INSTRUMENT')
            info['language'] = install.get('GLOBAL.LANGUAGE')
        except (OSError, yaml.YAMLError) as error:
            info['error'] = str(error).splitlines()[0]
        info['mtime'] = os.path.getmtime(install_path)
    info['files'] = [fname for fname in CONFIG_FILES
                     if os.path.isfile(os.path.join(path, fname))]
    return info


def list_profiles() -> List[Dict[str, Any]]:
    """
    List every registered profile (see profile_info)

    :return: list of dict, the profiles (newest first)
    """
    out = [profile_info(path, name) for name, path in
           read_profiles().items()]
    return sorted(out, key=lambda item: -(item.get('mtime') or 0))


def check_profile(path: Any) -> str:
    """
    Check a profile directory (has an install.yaml)

    :param path: Any, the profile directory

    :raises CommandError: if it is not an APERO profile

    :return: str, the absolute profile directory
    """
    path = os.path.realpath(os.path.expanduser(str(path or '')))
    if not os.path.isfile(os.path.join(path, base.INSTALL_YAML)):
        raise CommandError(str(textentry('SETUP_GUI_NO_PROFILE',
                                         args=[path])))
    return path


def _flatten(data: Any, prefix: str = '') -> Dict[str, Any]:
    """
    Flatten a nested dictionary to dotted keys (PATH: {RAW: x} -> PATH.RAW)

    :param data: Any, the (nested) dictionary
    :param prefix: str, the prefix of the keys

    :return: dict, dotted key -> value
    """
    out: Dict[str, Any] = dict()
    if not isinstance(data, dict):
        return out
    for key, value in data.items():
        name = '{0}.{1}'.format(prefix, key) if prefix else str(key)
        if isinstance(value, dict):
            out.update(_flatten(value, name))
        out[name] = value
    return out


def _load_yaml(path: str) -> Dict[str, Any]:
    """
    Load a yaml file (empty dict if missing or invalid)

    :param path: str, the yaml file

    :return: dict, the content
    """
    try:
        with open(path, 'r', encoding='utf-8') as yfile:
            data = yaml.safe_load(yfile)
    except (OSError, yaml.YAMLError):
        return dict()
    return data if isinstance(data, dict) else dict()


def profile_form(path: Any) -> Dict[str, Any]:
    """
    Get the setup form values of an existing profile (the same mapping as
    apero_setup.py --update: apero names from install.yaml /
    user_config.yaml, database names from database.yaml, setup choices
    from install.yaml SETUP_ARGUMENTS) - the password is never returned

    :param path: Any, the profile directory

    :raises CommandError: if it is not an APERO profile

    :return: dict, setup argument name -> value (plus dir_mode, profile)
    """
    path = check_profile(path)
    install = _load_yaml(os.path.join(path, base.INSTALL_YAML))
    config = _flatten(_load_yaml(os.path.join(path, 'user_config.yaml')))
    database = _flatten(_load_yaml(os.path.join(path,
                                                base.DATABASE_YAML)))
    form: Dict[str, Any] = dict(name=os.path.basename(path),
                                config_path=os.path.dirname(path))
    for name, sarg in SARGS.items():
        if name.upper() in SKIP_ARGS:
            continue
        # the same sources (and priority) as drs_setup.update_setup
        if sarg.apero_name and sarg.apero_name in install:
            form[name] = install[sarg.apero_name]
        if sarg.apero_name and sarg.apero_name in config:
            form[name] = config[sarg.apero_name]
        if sarg.database_name and sarg.database_name in database:
            form[name] = database[sarg.database_name]
    # the choices only stored in install.yaml
    for key, value in (install.get('SETUP_ARGUMENTS') or dict()).items():
        if key in SARGS and key not in ['NAME']:
            form[key] = value
    external = form.get('EXTERNAL_RAW')
    form['USE_EXTERNAL_RAW'] = external not in [None, '', 'None']
    # one data directory if every directory is its default sub-directory
    form['dir_mode'] = 'separate'
    raws = [form.get(key) for key in DIR_ARGS]
    if all(raws):
        parent = os.path.dirname(str(form.get('RAWDIR')))
        expected = {key: SARGS['DATADIR'].sets[key].format(DATADIR=parent)
                    for key in DIR_ARGS}
        if all(os.path.normpath(str(form.get(key))) == os.path.normpath(
                expected[key]) for key in DIR_ARGS):
            form['dir_mode'] = 'datadir'
            form['DATADIR'] = parent
    # the password stays on the server (taken from this profile if blank)
    form['pass_from_profile'] = path
    form['has_password'] = database.get('PASSWD') not in [None, '', 'None']
    return {key: (str(val) if isinstance(val, Path) else val)
            for key, val in form.items()}


# =============================================================================
# Define setup form functions
# =============================================================================
def _value(form: Dict[str, Any], name: str) -> Any:
    """
    Get a form value (the argument default when missing / blank)

    :param form: dict, the form
    :param name: str, the setup argument name

    :return: Any, the value (strings are stripped)
    """
    value = form.get(name)
    if isinstance(value, str):
        value = value.strip()
    if value in [None, '']:
        return SARGS[name].default_value
    return value


def _bool(value: Any) -> bool:
    """
    Convert a form value to a boolean (as the setup parser does)

    :param value: Any, the value

    :return: bool, the value
    """
    if isinstance(value, bool):
        return value
    return drs_setup.drs_text.true_text(value)


def _label(name: str) -> str:
    """
    Get the label of a setup argument for messages (NAME [--argname])

    :param name: str, the setup argument name

    :return: str, the label
    """
    return '{0} [{1}]'.format(name.upper(), SARGS[name].argname)


def _use_datadir(form: Dict[str, Any]) -> bool:
    """
    Whether the form uses one data directory (DATADIR) for every path

    :param form: dict, the form

    :return: bool, True for DATADIR mode
    """
    return str(form.get('dir_mode') or 'datadir') == 'datadir'


def setup_errors(form: Dict[str, Any]) -> List[str]:
    """
    Check a setup form (every problem is reported)

    :param form: dict, setup argument name -> value (plus dir_mode)

    :return: list of str, the problems (empty if the form is valid)
    """
    errors: List[str] = []
    # ---- required strings, restricted characters and options
    for name, sarg in SARGS.items():
        if name.upper() in SKIP_ARGS or name in DIR_ARGS + ['DATADIR']:
            continue
        # paths are checked below
        if name == 'config_path':
            continue
        if name in EXTERNAL_ARGS or name in TABLE_ARGS:
            continue
        value = _value(form, name)
        if sarg.required and value in [None, '', 'None']:
            errors.append(str(textentry('SETUP_GUI_REQUIRED',
                                        args=[_label(name)])))
            continue
        if value is None:
            continue
        bad = [char for char in restricted_chars(sarg)
               if char in str(value)]
        if bad:
            shown = ' '.join('space' if char == ' ' else char
                             for char in bad)
            errors.append(str(textentry('SETUP_GUI_BAD_CHAR',
                                        args=[_label(name), shown])))
        if sarg.dtype == 'int':
            try:
                value = int(value)
            except (TypeError, ValueError):
                errors.append(str(textentry('SETUP_GUI_NOT_INT',
                                            args=[_label(name), value])))
                continue
        if sarg.options is not None and sarg.dtype != 'bool':
            options = [str(opt) for opt in sarg.options]
            if str(value) not in options:
                errors.append(str(textentry(
                    'SETUP_GUI_BAD_OPTION',
                    args=[_label(name), value, ', '.join(options)])))
    # ---- paths must be absolute (they are written to config files)
    path_names = ['config_path']
    path_names += ['DATADIR'] if _use_datadir(form) else DIR_ARGS
    for name in path_names:
        value = _value(form, name)
        if value in [None, '', 'None']:
            errors.append(str(textentry('SETUP_GUI_REQUIRED',
                                        args=[_label(name)])))
        elif not os.path.isabs(os.path.expanduser(str(value))):
            errors.append(str(textentry('SETUP_GUI_NOT_ABSOLUTE',
                                        args=[_label(name), value])))
    # ---- the external raw directory must exist (it is never created)
    if _bool(form.get('USE_EXTERNAL_RAW')):
        external = _value(form, 'EXTERNAL_RAW')
        if not external or not os.path.isdir(os.path.expanduser(
                str(external))):
            errors.append(str(textentry('SETUP_GUI_NOT_DIR',
                                        args=[_label('EXTERNAL_RAW'),
                                              external or ''])))
        link = _value(form, 'EXTERNAL_RAW_TYPE')
        if str(link) not in setup_constants.EXTERNAL_RAW_TYPES:
            errors.append(str(textentry(
                'SETUP_GUI_BAD_OPTION',
                args=[_label('EXTERNAL_RAW_TYPE'), link,
                      ', '.join(setup_constants.EXTERNAL_RAW_TYPES)])))
    # ---- custom table names
    if _bool(form.get('EDIT_DBTABLES')):
        for name in TABLE_ARGS:
            value = _value(form, name)
            if value in [None, '', 'None']:
                errors.append(str(textentry('SETUP_GUI_REQUIRED',
                                            args=[_label(name)])))
            else:
                bad = [char for char in restricted_chars(SARGS['name'])
                       if char in str(value)]
                if bad:
                    errors.append(str(textentry(
                        'SETUP_GUI_BAD_CHAR',
                        args=[_label(name), ' '.join(bad)])))
    return errors


def profile_dir(form: Dict[str, Any]) -> Optional[str]:
    """
    Get the DRS_UCONFIG directory a setup form creates ({config}/{name},
    as drs_setup.fix_config_path)

    :param form: dict, the form

    :return: str or None, the profile directory (None if incomplete)
    """
    name = _value(form, 'name')
    config = _value(form, 'config_path')
    if not name or not config:
        return None
    config = os.path.realpath(os.path.expanduser(str(config)))
    if os.path.basename(config) == str(name):
        return config
    return os.path.join(config, str(name))


def _password(form: Dict[str, Any]) -> str:
    """
    Get the database password of a form (blank = keep the password of the
    profile the form was loaded from)

    :param form: dict, the form

    :return: str, the password ('None' if not set)
    """
    value = form.get('DATABASE_PASS')
    if value not in [None, '']:
        return str(value)
    source = form.get('pass_from_profile')
    if source:
        database = _load_yaml(os.path.join(str(source), base.DATABASE_YAML))
        if database.get('PASSWD') not in [None, '']:
            return str(database['PASSWD'])
    return str(SARGS['DATABASE_PASS'].default_value)


def setup_args(form: Dict[str, Any]) -> List[str]:
    """
    Get the apero_setup.py arguments of a (valid) setup form - every
    question apero_setup asks is answered so only reset / demo questions
    remain for the console

    :param form: dict, the form

    :return: list of str, the arguments (--argname=value)
    """
    args: List[str] = []
    use_datadir = _use_datadir(form)
    use_external = _bool(form.get('USE_EXTERNAL_RAW'))
    edit_tables = _bool(form.get('EDIT_DBTABLES'))
    for name, sarg in SARGS.items():
        if name.upper() in SKIP_ARGS:
            continue
        # either one data directory or every directory
        if name == 'DATADIR' and not use_datadir:
            continue
        if name in DIR_ARGS and use_datadir:
            continue
        # the external raw directory only when it is used
        if name in EXTERNAL_ARGS and not use_external:
            continue
        # table names only when customised (else {kind}_{NAME}_db)
        if name in TABLE_ARGS and not edit_tables:
            continue
        value = _value(form, name)
        if name == 'USE_EXTERNAL_RAW':
            value = use_external
        if value is None:
            continue
        # paths are absolute (as in install_script.sh)
        if sarg.dtype == 'path' or name == 'EXTERNAL_RAW':
            value = os.path.realpath(os.path.expanduser(str(value)))
        if sarg.dtype == 'bool':
            value = _bool(value)
        args.append('{0}={1}'.format(sarg.argname, value))
    return args


def _cli(script: str, args: List[str],
         env: Optional[Dict[str, str]] = None) -> str:
    """
    Get the CLI equivalent of a command (secrets masked)

    :param script: str, the script name
    :param args: list of str, the arguments
    :param env: dict or None, environment variables set for the command

    :return: str, the shell command
    """
    parts = []
    for key in sorted(env or dict()):
        value = MASK if key == drs_setup.DATABASE_PASS_ENV else env[key]
        parts.append('{0}={1}'.format(key, shlex.quote(value)))
    parts.append(script)
    parts += [shlex.quote(arg) for arg in args]
    return ' '.join(parts)


def setup_command(form: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the apero_setup.py command of the setup form

    :param form: dict, the form (see setup_errors)

    :raises CommandError: for invalid forms (all problems, one per line)

    :return: dict(cmd, display, env, profile)
    """
    errors = setup_errors(form)
    if errors:
        raise CommandError('\n'.join(errors))
    args = setup_args(form)
    env = {drs_setup.DATABASE_PASS_ENV: _password(form)}
    cmd = [sys.executable, str(SETUP_SCRIPT)] + args
    return dict(cmd=cmd, display=_cli('apero_setup.py', args, env), env=env,
                profile=profile_dir(form))


def update_command(path: Any, install_sh: bool = False) -> Dict[str, Any]:
    """
    Build the command re-running setup for a profile (apero_setup.py
    --update, the values come from the profile files) or regenerating its
    install_script.sh (--install_sh)

    :param path: Any, the profile directory
    :param install_sh: bool, only regenerate install_script.sh

    :raises CommandError: if it is not an APERO profile

    :return: dict(cmd, display, env, profile)
    """
    path = check_profile(path)
    mode = '--install_sh' if install_sh else '--update'
    args = [mode, '--name={0}'.format(os.path.basename(path)),
            '--config={0}'.format(path)]
    cmd = [sys.executable, str(SETUP_SCRIPT)] + args
    return dict(cmd=cmd, display=_cli('apero_setup.py', args), env=dict(),
                profile=path)


def validate_command(path: Any, reportfile: Optional[str] = None
                     ) -> Dict[str, Any]:
    """
    Build the apero_validate.py command of a profile

    :param path: Any, the profile directory
    :param reportfile: str or None, also write a state report here

    :raises CommandError: if it is not an APERO profile

    :return: dict(cmd, display, env, profile)
    """
    path = check_profile(path)
    args = [] if reportfile is None else ['--reportfile={0}'.format(
        reportfile)]
    env = {base.USER_ENV: path}
    cmd = [sys.executable, str(VALIDATE_SCRIPT)] + args
    return dict(cmd=cmd, display=_cli('apero_validate.py', args, env),
                env=env, profile=path)


# =============================================================================
# Define data manager functions
# =============================================================================
def check_setup_done(path: Any) -> str:
    """
    Check that apero_setup has been run for a profile (the files reset and
    the data manager need are there)

    :param path: Any, the profile directory

    :raises CommandError: if it is not a profile or setup has not been run

    :return: str, the profile directory (real path)
    """
    path = check_profile(path)
    missing = [name for name in SETUP_FILES
               if not os.path.isfile(os.path.join(path, name))]
    if missing:
        raise CommandError(str(textentry('SETUP_GUI_NOT_SETUP',
                                         args=[path, ', '.join(missing)])))
    return path


def data_dirs(path: Any) -> List[Dict[str, Any]]:
    """
    Get the data directories of a profile (from its user_config.yaml)

    :param path: Any, the profile directory

    :raises CommandError: if setup has not been run for the profile

    :return: list of dict(key, label, arg, path, exists, protected) - the
             profile directory itself comes last
    """
    path = check_setup_done(path)
    config = _flatten(_load_yaml(os.path.join(path, 'user_config.yaml')))
    out: List[Dict[str, Any]] = []
    for key, label, arg, protected in DATA_DIRS:
        value = config.get(key)
        # unset (e.g. no external raw directory)
        if value in [None, '', 'None']:
            continue
        dpath = os.path.realpath(os.path.expanduser(str(value)))
        out.append(dict(key=key, label=label, arg=arg, path=dpath,
                        exists=os.path.isdir(dpath), protected=protected))
    # the profile itself (DRS_UCONFIG)
    out.append(dict(key='DRS_UCONFIG', label='profile', arg=None,
                    path=path, exists=True, protected=False))
    return out


def dir_stats(path: str, seconds: float = STATS_SECONDS
              ) -> Dict[str, Any]:
    """
    Count the files and total size below a directory (stops after a time
    limit - raw directories can be very large)

    :param path: str, the directory
    :param seconds: float, the time limit

    :return: dict(nfiles, size, complete)
    """
    start = time.time()
    nfiles, size = 0, 0
    for root, _, names in os.walk(path):
        for name in names:
            try:
                # links count as themselves (not the file they point to)
                info = os.lstat(os.path.join(root, name))
            except OSError:
                continue
            nfiles += 1
            size += info.st_size
        if time.time() - start > seconds:
            return dict(nfiles=nfiles, size=size, complete=False)
    return dict(nfiles=nfiles, size=size, complete=True)


def reset_choices() -> List[Dict[str, Any]]:
    """
    Get the parts apero_reset.py can reset (with their help text)

    :return: list of dict(name, key, help)
    """
    out = []
    for name, key in RESET_PARTS:
        help_text = str(textentry('RESET_ONLY_{0}_HELP'.format(
            name.upper())))
        out.append(dict(name=name, key=key, help=help_text))
    return out


def reset_command(path: Any, part: Any = 'all', ask: bool = True,
                  nolog: bool = False) -> Dict[str, Any]:
    """
    Build the apero_reset.py command of a profile

    :param path: Any, the profile directory
    :param part: Any, 'all' or one of RESET_PARTS (--only_{part})
    :param ask: bool, if True apero_reset asks before each part (in the
                console), if False --nowarn
    :param nolog: bool, do not reset the log database (--nolog)

    :raises CommandError: if setup has not been run / unknown part

    :return: dict(cmd, display, env, profile)
    """
    path = check_setup_done(path)
    part = str(part or 'all')
    names = [name for name, _ in RESET_PARTS]
    if part != 'all' and part not in names:
        raise CommandError(str(textentry('SETUP_GUI_UNKNOWN',
                                         args=['reset part', part])))
    args: List[str] = []
    if part != 'all':
        args.append('--only_{0}'.format(part))
    if not ask:
        args.append('--nowarn')
    if nolog:
        args.append('--nolog')
    env = {base.USER_ENV: path}
    cmd = [sys.executable, str(RESET_SCRIPT)] + args
    return dict(cmd=cmd, display=_cli('apero_reset.py', args, env),
                env=env, profile=path)


# =============================================================================
# Define config file functions
# =============================================================================
def config_file(path: Any, name: Any) -> Tuple[str, bool]:
    """
    Get one of the files apero_setup writes into a profile

    :param path: Any, the profile directory
    :param name: Any, the file name (see CONFIG_FILES)

    :raises CommandError: for other files / non profiles

    :return: tuple, 1. the file path, 2. whether it may be edited
    """
    path = check_profile(path)
    name = str(name or '')
    if name not in CONFIG_FILES:
        raise CommandError(str(textentry('SETUP_GUI_NOT_CONFIG_FILE',
                                         args=[name])))
    return os.path.join(path, name), CONFIG_FILES[name]


def snapshot(path: Any) -> Dict[str, Optional[str]]:
    """
    Read every config file of a profile (to diff after re-running setup)

    :param path: Any, the profile directory

    :return: dict, file name -> text (None if missing)
    """
    path = check_profile(path)
    out: Dict[str, Optional[str]] = dict()
    for name in CONFIG_FILES:
        fpath = os.path.join(path, name)
        try:
            with open(fpath, 'r', encoding='utf-8',
                      errors='replace') as cfile:
                out[name] = cfile.read()
        except OSError:
            out[name] = None
    return out


# =============================================================================
# End of code
# =============================================================================

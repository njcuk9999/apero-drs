#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-26 at 15:54

@author: cook

Import Rules: Cannot use anything other than standard python 3 packages
(i.e. no numpy, no astropy etc)
"""
import argparse
import importlib
import os
import re
import signal
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import setup_lang

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'install.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = 'APERO'
# define the drs name (and module name)
DRS_PATH = 'apero'
# instruments
INSTRUMENTS = ['SPIROU', 'NIRPS_HA', 'NIRPS_HE']
# define the place where the constant recipes are
CONSTANTS_PATH = 'core.constants'
# define the place where the installation recipes are
INSTALL_PATH = 'tools.module.setup.drs_installation'
# define the drs_base path for language dict
BASE_PATH = 'base.drs_base'
# define the drs_asset  path for assets function
ASSET_PATH = 'tools.module.setup.drs_assets'
# Requirement files
REQ_USER = 'requirements_current.txt'
REQ_DEV = 'requirements_developer.txt'
VERSION_FILE = 'version.txt'
# explicit args
explicit_args = ['update', 'skip', 'dev', 'gui']
# Support database types
# TODO: Get from base
SUPPORTED_DATABASES = ['mysql+pymysql']
# modules that don't install like their name
module_translation = dict()
module_translation['Pillow'] = 'PIL'
module_translation['PyYAML'] = 'yaml'
module_translation['mysql-connector-python'] = 'mysql.connector'
module_translation['scikit-image'] = 'skimage'
module_translation['pandastable'] = ('pandastable', '0.13.0')
module_translation['GitPython'] = 'git'
module_translation['Bottleneck'] = 'bottleneck'
module_translation['SQLAlchemy'] = 'sqlalchemy'
module_translation['Sphinx'] = 'sphinx'
module_translation['ipython'] = 'IPython'
module_translation['gspread-pandas'] = 'gspread_pandas'
# start the language dictionary
lang = setup_lang.LangDict()


# =============================================================================
# Define functions
# =============================================================================
def get_version() -> str:
    filepath = os.path.abspath(__file__)
    # get files
    v_file = Path(filepath).parent.parent.joinpath(VERSION_FILE)
    # get version
    with open(v_file, 'r') as vfile:
        version = vfile.read().split('=')[-1].replace('\n', '')
    # return version
    return version


# set version
__version__ = get_version()


# need this argument before anything else
def get_sys_arg(name, kind=None):
    """
    A prescreening for arguments needed before argparse

    :param name:
    :param kind:
    :return:
    """
    # get the command line arguments from sys.argv
    args = sys.argv[1:]
    # loop around arguments and look for argument "name"
    for it, arg in enumerate(args):
        # if "name" is in the arguments
        if name in arg:
            # if we have a switch return True
            if kind == 'switch':
                return True
            # if we have an equals the value of the arg is the second half
            elif '=' in arg:
                return arg.split('=')[-1]
            # if we have arguments after the value is the next argument
            elif len(args) > it + 1:
                return args[it + 1]
            # else we return None --> no argument
            else:
                return None
    # if we have a switch and argument not found we return False
    if kind == 'switch':
        return False
    # else we return None --> no argument
    else:
        return None


def get_apero():
    """
    Get the apero module (sounds like a given but need to check)
    :return:
    """
    # start with file definition
    start = Path(__file__).absolute()
    # get apero working directory
    drs_path = start.parent.parent
    # make aboslute
    drs_path = drs_path.absolute()
    # try to import to raise exception
    try:
        # add drs path to sys
        sys.path.append(str(drs_path))
        _ = importlib.import_module(DRS_PATH)
    except Exception as _:
        path = drs_path.joinpath(DRS_PATH)
        raise ImportError('Import Error: Cannot find {0}'.format(path))
    return drs_path


def catch_sigint(signal_received: Any, frame: Any):
    """
    Deal with Keyboard interupt --> do a sys.exit

    :param signal_received: Any, not used (but expected)
    :param frame: Any, not used (but expected)

    :return: None, exits if this function is called
    """
    # we don't use these we just exit
    _ = signal_received, frame
    # print: Exiting installation script
    print(lang.error('40-001-00075'))
    # raise Keyboard Interrupt
    sys.exit()


def extract_package_info(line: str
                         ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    # match string like 'package @ URL'
    match_string = r'^\s*([\w-]+)\s*@.*'
    # Check if the line has the format 'package @ URL'
    if re.match(match_string, line):
        package_name = line.split('@')[0].strip()
        source = line.split('@')[1].strip()
        return package_name, '@', source

    # match string like 'package == version_spec'
    match_string = r'^([\w-]+)\s*(?:(==|>=|<=|>|<)\s*([\w\d.\-]+))?.*'
    # Check if the line has the format 'package version_spec'
    package_info = re.match(match_string, line)
    if package_info:
        package_name = package_info.group(1)
        version_operator = package_info.group(2)
        version = package_info.group(3)
        return package_name, version_operator, version
    return None, None, None



def load_requirements(requirements_file: Union[str, Path]
                      ) -> Dict[str, Tuple[str, str]]:
    # store modules
    modules = dict()
    # open the requirements file
    with open(requirements_file, 'r') as req_file:
        lines = req_file.readlines()
    # loop around all lines
    for line in lines:
        # skip blank and commented lines
        if line.strip() and not line.strip().startswith('#'):
            package_name, version_operator, version = extract_package_info(line)
            if package_name is not None:
                modules[package_name] = (version_operator, version)
    # return the modules
    return modules


def validate(devmode: bool = False):
    """
    Check whether users system satisfies all python module requirements

    :raises SystemExit: if modules are not correct
    :return: None
    """
    # python version check
    if sys.version_info.major < 3:
        # log error: Fatal Error: Python 2 is not supported
        print(lang.error('00-000-00009'))
        sys.exit()
    # ------------------------------------------------------------------
    # load requirement files
    # ------------------------------------------------------------------
    filepath = os.path.abspath(__file__)
    # get files
    user_req_file = Path(filepath).parent.parent.joinpath(REQ_USER)
    dev_req_file = Path(filepath).parent.parent.joinpath(REQ_DEV)
    # get lists of modules
    if devmode:
        modules = load_requirements(dev_req_file)
    else:
        modules = load_requirements(user_req_file)

    # storage of checked modules
    checked = []
    # log check: Module check
    print(lang['40-001-00076'])
    # all checks passed
    passed = True
    # ------------------------------------------------------------------
    # loop around required modules to check
    # ------------------------------------------------------------------
    for modname in modules:
        # remove end of lines
        operator, version = modules[modname]
        # skip operators we cannot check
        if operator not in ['==', '>=', '<=', '>', '<']:
            continue
        # get suggested installation module
        suggested = 'pip install {0}{1}{2}'.format(modname, operator, version)
        # deal with modules with different import name
        if modname in module_translation:
            if isinstance(module_translation[modname], tuple):
                modname, modversion = module_translation[modname]
            else:
                modname = module_translation[modname]
        # deal with checked
        if modname in checked:
            continue
        else:
            checked.append(modname)
        # ------------------------------------------------------------------
        # test importing module
        # noinspection PyBroadException
        try:
            imod = importlib.import_module(modname)
            # --------------------------------------------------------------
            # check the version
            check_version(modname, imod, version.split('.'), suggested)
        # --------------------------------------------------------------
        except Exception as _:
            # Fatal Error: {0} requires module {1} to be installed
            eargs = [DRS_PATH, modname, suggested]
            print(lang.error('00-000-00011').format(*eargs))
            passed = False
    # only break if we have a failed module
    if not passed:
        print('Module check did not pass')
        sys.exit()


def check_install() -> Tuple[Any, Any, Any]:
    """
    Check for apero installation directory

    :raises ImportError: if unable to find apero installation
    :return: tuple, 1. the apero.constants sub-module, 2. the apero.installation
             module
    """
    # get apero
    drs_path = get_apero()
    # construct module names
    constants_mod = '{0}.{1}'.format(DRS_PATH, CONSTANTS_PATH)
    install_mod = '{0}.{1}'.format(DRS_PATH, INSTALL_PATH)
    base_mod = '{0}.{1}'.format(DRS_PATH, BASE_PATH)
    # try to import the modules
    try:
        constants = importlib.import_module(constants_mod)
    except Exception as _:
        # raise error
        raise ImportError(lang.error('00-000-00013').format(constants_mod))
    try:
        install = importlib.import_module(install_mod)
    except Exception as _:
        # raise error
        raise ImportError(lang.error('00-000-00013').format(install_mod))
    try:
        drs_base = importlib.import_module(base_mod)
    except Exception as _:
        # raise error
        raise ImportError(lang.error('00-000-00013').format(base_mod))
    # add apero to the PYTHONPATH
    if 'PYTHONPATH' in os.environ:
        oldpath = os.environ['PYTHONPATH']
        os.environ['PYTHONPATH'] = str(drs_path) + os.pathsep + oldpath
    # else we just add it to current PYTHON PATH
    else:
        os.environ['PYTHONPATH'] = str(drs_path)
        # add to active path
        sys.path = [str(drs_path)] + sys.path
    # if we have reached this point we can break out of the while loop
    return constants, install, drs_base


def get_args() -> argparse.Namespace:
    """
    Define the command line arguments (via argparse) for this recipe
    :return:
    """
    # get parser
    description = lang['INSTALL_DESCRIPTION']
    parser = argparse.ArgumentParser(description=description.format(DRS_PATH))
    # add arguments
    parser.add_argument('--update', '--upgrade', action='store_true',
                        default=False, dest='update',
                        help=lang['INSTALL_UPDATE_HELP'])
    parser.add_argument('--skip', action='store_true', default=False,
                        dest='skip', help=lang['INSTALL_SKIP_HELP'])
    parser.add_argument('--dev', action='store_true', default=False,
                        dest='dev', help=lang['INSTALL_DEV_HELP'])
    parser.add_argument('--gui', action='store_true', default=False, dest='gui',
                        help=lang['INSTALL_GUI_HELP'])
    parser.add_argument('--name', action='store', dest='name',
                        help=lang['INSTALL_NAME_HELP'])
    # add directory args
    parser.add_argument('--root', action='store', dest='root',
                        help=lang['INSTALL_ROOT_HELP'])
    parser.add_argument('--config', action='store', dest='config',
                        help=lang['INSTALL_CONFIG_HELP'])
    parser.add_argument('--instrument', action='store', dest='instrument',
                        help=lang['INSTALL_INSTRUMENT_HELP'],
                        choices=INSTRUMENTS)
    parser.add_argument('--datadir', action='store', dest='datadir',
                        help=lang['INSTALL_DATADIR_HELP'])
    parser.add_argument('--rawdir', action='store', dest='rawdir',
                        help=lang['INSTALL_RAWDIR_HELP'])
    parser.add_argument('--tmpdir', action='store', dest='tmpdir',
                        help=lang['INSTALL_TMPDIR_HELP'])
    parser.add_argument('--reddir', action='store', dest='reddir',
                        help=lang['INSTALL_REDDIR_HELP'])
    parser.add_argument('--outdir', action='store', dest='outdir',
                        help=lang['INSTALL_OUTDIR_HELP'])
    parser.add_argument('--calibdir', action='store', dest='calibdir',
                        help=lang['INSTALL_CALIBDIR_HELP'])
    parser.add_argument('--telludir', action='store', dest='telludir',
                        help=lang['INSTALL_TELLUDIR_HELP'])
    parser.add_argument('--plotdir', action='store', dest='plotdir',
                        help=lang['INSTALL_PLOTDIR_HELP'])
    parser.add_argument('--rundir', action='store', dest='rundir',
                        help=lang['INSTALL_RUNDIR_HELP'])
    parser.add_argument('--assetsdir', action='store', dest='assetsdir',
                        help=lang['INSTALL_ASSETDIR_HELP'])
    parser.add_argument('--logdir', action='store', dest='logdir',
                        help=lang['INSTALL_LOGDIR_HELP'])
    parser.add_argument('--otherdir', action='store', dest='otherdir',
                        help='Other Directory')
    parser.add_argument('--lbldir', action='store', dest='lbldir',
                        help='LBL Directory')
    parser.add_argument('--always_create', action='store', dest='always_create',
                        help='Always create directories that do not exist. '
                             'Do not prompt.')
    # add tar file for assets
    parser.add_argument('--assets_tar', action='store', dest='tar_file',
                        help='Path to the assets tar file '
                             '(if not set downloads from servers)')
    # add plot mode argument
    parser.add_argument('--plotmode', action='store', dest='plotmode',
                        help=lang['INSTALL_PLOTMODE_HELP'],
                        choices=['0', '1', '2'])
    # add cleaning argument
    parser.add_argument('--clean', action='store', dest='clean',
                        help=lang['INSTALL_CLEAN_HELP'])
    # add argument to skip cleaning check
    parser.add_argument('--clean_no_warning', action='store',
                        dest='clean_no_warning',
                        help=lang['INSTALL_CLEAN_NO_WARNING_HELP'])
    # add database mode argument
    parser.add_argument('--database_type', action='store', dest='database_type',
                        help=lang['INSTALL_DBMODE_HELP'],
                        choices=SUPPORTED_DATABASES,
                        type=str)
    # add MySQL database arguements (database_mode = 2)
    parser.add_argument('--database_host', action='store', dest='database_host',
                        help=lang['INSTALL_DB_HOST_HELP'])
    parser.add_argument('--database_user', action='store', dest='database_user',
                        help=lang['INSTALL_DB_USER_HELP'])
    parser.add_argument('--database_pass', action='store', dest='database_pass',
                        help=lang['INSTALL_DB_PASS_HELP'])
    parser.add_argument('--database_name', action='store', dest='database_name',
                        help=lang['INSTALL_DB_NAME_HELP'])
    parser.add_argument('--calibtable', action='store', dest='calibtable',
                        help=lang['INSTALL_CALIBTABLE_HELP'])
    parser.add_argument('--tellutable', action='store', dest='tellutable',
                        help=lang['INSTALL_TELLUTABLE_HELP'])
    parser.add_argument('--findextable', action='store', dest='findextable',
                        help=lang['INSTALL_INDEXTABLE_HELP'])
    parser.add_argument('--logtable', action='store', dest='logtable',
                        help=lang['INSTALL_LOGTABLE_HELP'])
    parser.add_argument('--astromtable', action='store', dest='astromtable',
                        help=lang['INSTALL_OBJTABLE_HELP'])
    parser.add_argument('--rejecttable', action='store', dest='rejecttable',
                        help=lang['INSTALL_REJECTTABLE_HELP'])
    parser.add_argument('--langtable', action='store', dest='langtable',
                        help=lang['INSTALL_LANGTABLE_HELP'])
    # parse arguments
    args = parser.parse_args()
    return args


def save_args(args: argparse.Namespace):
    """
    Save argument list to file (in the config directory) this allows knowing
    what parameters were used and running the profile again with the same
    settings

    :param args: argparse.Namespace - from argparse (but with updated
                 values after user input)
    :return: None, writes to disk
    """
    # write command
    command = f'python {__NAME__}          \\'
    # set always create to true (even if False)
    args.always_create = True
    # remove profile name from config path (for arguments)
    #   but keep config_path for saving file to
    config_path = str(args.config)
    if str(args.config).endswith(args.name):
        args.config = str(args.config)[:-len(args.name)]
    # convert namespace to dictionary
    argdict = vars(args)
    # add non null arguments
    for it, arg in enumerate(argdict):
        # only add arguments which are not still None
        if argdict[arg] is not None:
            # set up command prefix
            prefix = '\n' + 10 * ' '
            # set up command suffix
            if it != len(argdict) - 1:
                suffix = ' ' * 4 + '\\'
            else:
                suffix = ''
            # add command
            # deal with explicit argument (no value)
            if arg in explicit_args:
                if argdict[arg]:
                    command += prefix + f'--{arg}' + suffix
            # deal with strings (need to worry about white spaces)
            elif isinstance(argdict[arg], (str, Path)):
                command += prefix + f'--{arg}="{argdict[arg]}"' + suffix
            # deal with everything else (just convert to string)
            else:
                command += prefix + f'--{arg}={str(argdict[arg])}' + suffix
    # construct path
    path = os.path.join(config_path, 'install.sh')
    # write to file
    with open(path, 'w') as afile:
        afile.write(command)
    # return the path (for printing)
    return path


def check_version(module: str, imod: Any, rversionlist: Union[List[str], None],
                  suggested: str, required: bool = True):
    """
    Check a module version

    :param module: str, module name
    :param imod: Module imported
    :param rversionlist: list of strings, the required version, subversion etc
                         could be ['1'], ['1', '1'], or ['1', '1', '1'] etc
                         for version 1, 1.1, 1.1.1  etc
    :param suggested: str, the suggested version
    :param required: bool, if True this module is required and code will exit
                     if version is not satisfied

    :raises SystemExit: if module is required and not valid

    :return: None, prints if module is valid or suggested
    """
    # test version
    passed = False
    # ------------------------------------------------------------------
    # if we don't have a required version to test don't test passed here
    if rversionlist is None:
        return True, None
    # ------------------------------------------------------------------
    # test minimum version of module
    if hasattr(imod, '__version__'):
        # get the version
        version = getattr(imod, '__version__').split('.')
        # loop around rversion list
        for v_it, rversion in enumerate(rversionlist):
            # convert rversion to int
            # noinspection PyBroadException
            try:
                rversion = int(rversion)
            except Exception as _:
                break
            # if we don't have a level this deep break
            if len(version) < (v_it - 1):
                break
            # try to make an integer
            # noinspection PyBroadException
            try:
                version[v_it] = int(version[v_it])
            except Exception as _:
                break
            # if version is higher pass
            if version[v_it] > rversion:
                passed = True
                break
            # if version is the same skip to lower level
            elif version[v_it] == rversion:
                passed = True
                continue
            # if version is lower fail
            else:
                passed = False
                break
        # --------------------------------------------------------------
        # get string lists
        rstrlist = list(map(lambda x: str(x), rversionlist))
        strlist = list(map(lambda x: str(x), version))
        # --------------------------------------------------------------
        # get args
        args = [DRS_PATH, module, '.'.join(rstrlist), '.'.join(strlist),
                suggested]
        # if we have not passed print fail message
        if not passed and not required:
            # print: {0} recommends {1} to be updated ({3} < {2})
            print(lang['40-001-00079'].format(*args))
        elif not passed:
            # print: Fatal Error: {0} requires module {1} ({3} < {2})
            raise ImportError(lang.error('00-000-00011').format(*args))
        else:
            # print: Passed: {1} ({3} >= {2})
            print(lang['40-001-00081'].format(*args))


# =============================================================================
# Define main function
# =============================================================================
def main():
    """
    Run the installation

    :return:
    """
    global lang
    # set function name
    func_name = __NAME__ + '.main()'
    # -------------------------------------------------------------------------
    # get language argument
    langarg = get_sys_arg('lang')
    if langarg in setup_lang.LANGUAGES:
        lang = setup_lang.LangDict(langarg)
    else:
        lang = setup_lang.LangDict()
    language = lang.language
    # ----------------------------------------------------------------------
    # deal with validation
    if not get_sys_arg('--skip') and not get_sys_arg('--help', 'switch'):
        if get_sys_arg('--dev'):
            validate(devmode=True)
        else:
            validate()
    # catch Ctrl+C
    signal.signal(signal.SIGINT, catch_sigint)
    # get install paths
    constants, install, drs_base = check_install()
    # this is so we have direct access in IDE to modules
    # noinspection PyBroadException
    try:
        from apero.tools.module.setup import drs_installation as install
        from apero.core import constants
        from apero.base import drs_base
    except Exception as _:
        pass
    # update the language dict to use the full proxy database
    lang = drs_base.lang_db_proxy()
    # get text entry for remaining text
    textentry = install.textentry
    # ----------------------------------------------------------------------
    # get arguments
    args = get_args()
    # ----------------------------------------------------------------------
    # start up
    # ----------------------------------------------------------------------
    # get global parameters
    params = constants.load(from_file=False)
    # ----------------------------------------------------------------------
    # Start of user setup
    # ----------------------------------------------------------------------
    # if gui pass for now
    if args.gui:
        install.cprint(textentry('40-001-00066'))
        sys.exit()
    # get parameters from user input
    elif not args.update:
        allparams, args = install.user_interface(params, args, language)
        # save current arguments to disk
        afile = save_args(args)
        install.cprint(f'Saved installation parameters to: {afile}')
    else:
        allparams = install.update(params, args)
    # add environmental variable DRS_UCONFIG
    os.environ['DRS_UCONFIG'] = str(allparams['USERCONFIG'])
    # reload params
    params = constants.load(allparams['INSTRUMENT'], from_file=False)
    params.set('PID', value='0', source=func_name)
    # ----------------------------------------------------------------------
    # End of user setup
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Installation
    # ----------------------------------------------------------------------
    # print installing title
    print('\n\n\n')
    install.cprint(install.printheader(), 'm')
    install.cprint(textentry('40-001-00067'), 'm')
    install.cprint(install.printheader(), 'm')
    print('\n')
    # ----------------------------------------------------------------------
    # get binary paths
    install.cprint(textentry('40-001-00068'), 'm')
    allparams = install.bin_paths(params, allparams)
    # ----------------------------------------------------------------------
    # copy config files to config dir
    install.cprint(textentry('40-001-00069'), 'm')
    allparams = install.create_configs(params, allparams)
    # ----------------------------------------------------------------------
    # # update config values from iparams
    # install.cprint(textentry('40-001-00070'), 'm')
    # allparams = install.update_configs(allparams)
    # ----------------------------------------------------------------------
    # create source files to add environmental variables
    install.cprint(textentry('40-001-00071'), 'm')
    allparams = install.create_shell_scripts(params, allparams)
    # ----------------------------------------------------------------------
    # download the assets (into github directory)
    try:
        from apero.tools.module.setup import drs_assets
    except Exception as _:
        assets_mod = '{0}.{1}'.format(DRS_PATH, ASSET_PATH)
        try:
            drs_assets = importlib.import_module(assets_mod)
        except Exception as _:
            # raise error
            raise ImportError(lang.error('00-000-00013').format(assets_mod))
    # now check whether we need to download the assets
    update_assets = drs_assets.check_local_assets(params)
    if update_assets:
        drs_assets.update_local_assets(params, tarfile=allparams['TARFILE'])
    # ----------------------------------------------------------------------
    # perform clean install on each instrument if requested
    install.cprint(textentry('40-001-00072'), 'm')
    allparams = install.clean_install(params, allparams)
    if allparams is None:
        print('\n\n\n')
        install.cprint(install.printheader(), 'r')
        install.cprint(textentry('40-001-00075'), 'r')
        install.cprint(install.printheader(), 'r')
        print('\n')
        return
    # ----------------------------------------------------------------------
    # create sym links for all recipes
    install.cprint(textentry('40-001-00073'), 'm')
    allparams = install.create_symlinks(params, allparams)
    # ----------------------------------------------------------------------
    # display message
    install.print_options(params, allparams)
    # ----------------------------------------------------------------------
    # log that installation is complete
    print('\n\n\n')
    install.cprint(install.printheader(), 'm')
    install.cprint(textentry('40-001-00074'), 'm')
    install.cprint(install.printheader(), 'm')
    print('\n')


# =============================================================================
# Start of code
# =============================================================================
# Run main code here
if __name__ == '__main__':
    main()

# =============================================================================
# End of code
# =============================================================================

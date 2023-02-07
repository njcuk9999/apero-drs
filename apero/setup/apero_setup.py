#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-26 at 15:54

@author: cook

Import Rules: Cannot use anything other than standard python 3 packages and apero
(i.e. no numpy, no astropy etc)
"""
import argparse
import importlib
import os
from pathlib import Path
import signal
import sys
from typing import Any, List, Union

from apero.tools.module.setup import drs_installation as install
from apero.core import constants
from apero.base import drs_base, base
from apero.setup import setup_lang
from apero.setup.utils import catch_sigint

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_setup.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
# instruments
INSTRUMENTS = base.INSTRUMENTS[:-1]  # Remove "None"
# define the drs name (and module name)
DRS_PATH = 'apero'
# modules that don't install like their name
module_translation = dict()
module_translation['Pillow'] = 'PIL'
module_translation['pyyaml'] = 'yaml'
module_translation['mysql-connector-python'] = 'mysql.connector'
module_translation['scikit-image'] = 'skimage'
module_translation['importlib-resources'] = 'importlib_resources'
module_translation['pandastable'] = ('pandastable', '0.12.2')
# start the language dictionary
lang = setup_lang.LangDict()


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


def validate():
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
    # get lists of modules
    main_req = load_requirements(base.RECOMM_USER)
    mode = ["main"] * len(main_req)
    mysql_req = load_requirements(base.RECOMM_MYSQL)
    mode += ["mysql"] * len(mysql_req)
    dev_req = load_requirements(base.RECOMM_DEV)
    mode += ["dev"] * len(dev_req)
    modules = main_req + mysql_req + dev_req
    # storage of checked modules
    checked = []
    # log check: Module check
    print(lang['40-001-00076'])
    # ------------------------------------------------------------------
    # loop around required modules to check
    # ------------------------------------------------------------------
    for m_it, module in enumerate(modules):
        # remove end of lines
        module = module.replace('\n', '')
        # get module name
        try:
            modname = module.split('==')[0]
            modversion = module.split('==')[1].split('.')
        except Exception as e:
            # Module name "{0}" error {1}: {2}'
            emsg = lang.error('00-000-00010')
            eargs = [module, type(e), str(e)]
            raise IndexError(emsg.format(*eargs))
        # get suggested installation module
        suggested = lang['40-001-00077'].format(module)
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
            check_version(module, imod, modversion, suggested,
                          required=mode[m_it] == "main")
        # --------------------------------------------------------------
        except Exception as _:
            if mode[m_it] != "main":
                # {0} recommends {1} to be installed (dev only)'
                print(lang['40-001-00078'].format(DRS_PATH, module, suggested))
            else:
                # Fatal Error: {0} requires module {1} to be installed
                eargs = [DRS_PATH, module, suggested]
                print(lang.error('00-000-00011').format(*eargs))
                sys.exit()


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
                        dest='devmode', help=lang['INSTALL_DEV_HELP'])
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
    parser.add_argument('--always_create', action='store', dest='alwayscreate',
                        help='Always create directories that do not exist. '
                             'Do not prompt.')
    # add plot mode argument
    parser.add_argument('--plotmode', action='store', dest='plotmode',
                        help=lang['INSTALL_PLOTMODE_HELP'],
                        choices=['0', '1', '2'])
    # add cleaning argument
    parser.add_argument('--clean', action='store', dest='clean',
                        help=lang['INSTALL_CLEAN_HELP'])
    # add argument to skip cleaning check
    parser.add_argument('--clean_no_warning', action='store', dest='cleanwarn',
                        help=lang['INSTALL_CLEAN_NO_WARNING_HELP'])
    # add database mode argument
    parser.add_argument('--database_mode', action='store', dest='database_mode',
                        help=lang['INSTALL_DBMODE_HELP'], choices=[1, 2],
                        type=int)
    # add MySQL database arguements (database_mode = 2)
    parser.add_argument('--database_host', action='store', dest='database_host',
                        help=lang['INSTALL_DB_HOST_HELP'])
    parser.add_argument('--database_user', action='store', dest='database_user',
                        help=lang['INSTALL_DB_USER_HELP'])
    parser.add_argument('--database_pass', action='store', dest='database_pass',
                        help=lang['INSTALL_DB_PASS_HELP'])
    parser.add_argument('--database_name', action='store', dest='database_name',
                        help=lang['INSTALL_DB_NAME_HELP'])
    parser.add_argument('--calib-table', action='store', dest='calibtable',
                        help=lang['INSTALL_CALIBTABLE_HELP'])
    parser.add_argument('--tellu-table', action='store', dest='tellutable',
                        help=lang['INSTALL_TELLUTABLE_HELP'])
    parser.add_argument('--index-table', action='store', dest='indextable',
                        help=lang['INSTALL_INDEXTABLE_HELP'])
    parser.add_argument('--log-table', action='store', dest='logtable',
                        help=lang['INSTALL_LOGTABLE_HELP'])
    parser.add_argument('--obj-table', action='store', dest='objtable',
                        help=lang['INSTALL_OBJTABLE_HELP'])
    parser.add_argument('--reject-table', action='store', dest='rejecttable',
                        help=lang['INSTALL_REJECTTABLE_HELP'])
    parser.add_argument('--lang-table', action='store', dest='langtable',
                        help=lang['INSTALL_LANGTABLE_HELP'])
    # parse arguments
    args = parser.parse_args()
    return args


def load_requirements(filename: Union[str, Path]) -> List[str]:
    """
    Load requirements from file

    :return: list of strings, return a list of required modules and versions
             (from a pip style requirements.txt)
    """
    # storage for list of modules
    modules = []
    # open requirements file
    with open(filename, 'r') as rfile:
        lines = rfile.readlines()
    # get modules from lines in requirements file
    for line in lines:
        if len(line.strip()) == 0:
            continue
        if line.startswith('#'):
            continue
        else:
            modules.append(line)
    # return modules
    return modules


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
            print(lang.error('40-001-00080').format(*args))
            sys.exit()
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
    # -----------------------------------------------------------------------------
    # get language argument
    langarg = get_sys_arg('lang')
    if langarg in setup_lang.LANGUAGES:
        lang = setup_lang.LangDict(langarg)
    else:
        lang = setup_lang.LangDict()
    LANGUAGE = lang.language
    # ----------------------------------------------------------------------
    # deal with validation
    if not get_sys_arg('--skip') and not get_sys_arg('--help', 'switch'):
        validate()
    # catch Ctrl+C
    signal.signal(signal.SIGINT, catch_sigint)
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
        allparams, args = install.user_interface(params, args, LANGUAGE)
    else:
        allparams = install.update(params, args)
    # add environmental variable DRS_UCONFIG
    os.environ['DRS_UCONFIG'] = str(allparams['USERCONFIG'])
    # reload params
    params = constants.load(allparams['INSTRUMENT'], from_file=False)
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
    # TODO: Update message and add to language database (just root path now)
    install.cprint(textentry('40-001-00068'), 'm')
    allparams = install.root_path(params, allparams)
    # ----------------------------------------------------------------------
    # copy config files to config dir
    install.cprint(textentry('40-001-00069'), 'm')
    allparams = install.create_configs(params, allparams)
    # ----------------------------------------------------------------------
    # Add configuration file in user home to map profile name -> config path
    # TODO: Add message to language database for this step
    allparams = install.update_home_profiles(params, allparams)
    # ----------------------------------------------------------------------
    # update config values from allparams
    install.cprint(textentry('40-001-00070'), 'm')
    allparams = install.update_configs(allparams)
    # ----------------------------------------------------------------------
    # create source files to add environmental variables
    install.cprint(textentry('40-001-00071'), 'm')
    allparams = install.create_shell_scripts(params, allparams)
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

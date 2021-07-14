#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-26 at 15:54

@author: cook
"""
import argparse
import importlib
import os
from pathlib import Path
import signal
import sys
from typing import Any, List, Tuple, Union


# =============================================================================
# Define variables
# =============================================================================
# define the drs name (and module name)
DRS_PATH = 'apero'
# LANGUAGE
# TODO: allow as argument (This will then change all text)
LANGUAGE = 'ENG'
# define the place where the constant recipes are
CONSTANTS_PATH = 'core.constants'
# define the place where the installation recipes are
INSTALL_PATH = 'tools.module.setup.drs_installation'
# Requirement files
REQ_USER = 'requirements_current.txt'
REQ_DEV = 'requirements_developer.txt'

# modules that don't install like their name
module_translation = dict()
module_translation['Pillow'] = 'PIL'
module_translation['pyyaml'] = 'yaml'
module_translation['mysql-connector-python'] = 'mysql.connector'
module_translation['scikit-image'] = 'skimage'


# =============================================================================
# Define functions
# =============================================================================
def get_args() -> argparse.Namespace:
    """
    Define the command line arguments (via argparse) for this recipe
    :return:
    """
    # get parser
    description = ' Install {0} software for reducing observational data'
    parser = argparse.ArgumentParser(description=description.format(DRS_PATH))

    parser.add_argument('--update', '--upgrade', action='store_true',
                        default=False, dest='update',
                        help=' updates installation (not clean install) and '
                             'checks for updates to your current config files')
    parser.add_argument('--skip', action='store_true', default=False,
                        dest='skip',
                        help='skip the python module checks '
                             '(Not recommended for first time installation)')
    parser.add_argument('--dev', action='store_true', default=False,
                        dest='devmode',
                        help='activate developer mode (prompts for all '
                             'config/constant groups and add them to your '
                             'config/constant files)')
    parser.add_argument('--gui', action='store_true', default=False,
                        dest='gui',
                        help='use GUI to install (Not yet supported) ')
    parser.add_argument('--name', action='store', dest='name',
                        help='The name for this specific installation'
                             '(Allows the creation of multiple profiles with'
                             ' different settings)')

    # add directory args
    parser.add_argument('--root', action='store', dest='root',
                        help='The installation directory (if not given tries'
                             'to find the path and if not found prompts '
                             'the user)')
    parser.add_argument('--config', action='store', dest='config',
                        help='The user configuration path (if not given '
                             'prompts the user)')
    parser.add_argument('--instrument', action='store', dest='instrument',
                        help='The instrument to install (if not given '
                             'prompts the user for each available instrument).'
                             'THIS ARGUMENT IS REQUIRED TO SET --datadir, '
                             '--rawdir, --tmpdir, --reddir, --calibdir, '
                             '--telludir, --plotdir, --rundir, --assetdir, '
                             '--logdir',
                        choices=['SPIROU'])
    parser.add_argument('--datadir', action='store', dest='datadir',
                        help='The data directory (if given overrides all '
                             'sub-data directories - i.e. raw/tmp/red/plot) '
                             'if not given and other paths not given prompts'
                             'the user for input.')
    parser.add_argument('--rawdir', action='store', dest='rawdir',
                        help='The raw directory where input files are stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--tmpdir', action='store', dest='tmpdir',
                        help='The tmp directory where preprocessed files are '
                             'stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--reddir', action='store', dest='reddir',
                        help='The reduced directory where output files are '
                             'stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--outdir', action='store', dest='outdir',
                        help='The post process directory where output files are '
                             'stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--calibdir', action='store', dest='calibdir',
                        help='The calibration database directory where '
                             'calibrations used in the database files '
                             'are stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--telludir', action='store', dest='telludir',
                        help='The telluric database directory where telluric '
                             'database files are stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--plotdir', action='store', dest='plotdir',
                        help='The plot directory where plots/summary documents '
                             'are stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--rundir', action='store', dest='rundir',
                        help='The run directory where run/batch files are '
                             'stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--assetsdir', action='store', dest='assetsdir',
                        help='The assets directory where assets files are '
                             'stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    parser.add_argument('--logdir', action='store', dest='logdir',
                        help='The log directory where log and lock files are '
                             'stored.'
                             '(if not given and --datadir not given prompts'
                             'the user to input if user chooses to install '
                             'each directory separately)')
    # add plot mode argument
    parser.add_argument('--plotmode', action='store', dest='plotmode',
                        help='The plot mode. 0=Summary plots only '
                             '1=Plot at end of run 2=Plot at creation '
                             '(pauses code). If unset user is prompted for '
                             'choice.',
                        choices=['0', '1', '2'])
    # add cleaning argument
    parser.add_argument('--clean', action='store', dest='clean',
                        help='Whether to run from clean directories - '
                             'RECOMMENDED - clears out old files and copies'
                             'over all required default data files. '
                             'If unset user is prompted for  choice.')
    # add argument to skip cleaning check
    parser.add_argument('--clean_no_warning', action='store', dest='cleanwarn',
                        help='Whether to warn about cleaning populated '
                             'directories - WARNING if set to True will delete '
                             'all tmp/reduced/calibDB etc. data without prompt')
    # add argument with ds9 path
    parser.add_argument('--ds9path', action='store', dest='ds9path',
                        help='Optionally set the ds9 path (used in some tools)')
    # add argument with pdf latex path
    parser.add_argument('--pdflatexpath', action='store', dest='pdfpath',
                        help='Optionally set the pdf latex path (used to '
                             'produce summary plots. '
                             'If unset user is prompted for choice.'
                             'If still unset user will only have html summary'
                             'document not a pdf one.')
    # add database mode argument
    parser.add_argument('--database_mode', action='store', dest='database_mode',
                        help='Database mode (1: sqlite, 2: mysql). '
                             'If unset user is prompted for choice.',
                        choices=[1, 2], type=int)
    # add MySQL database arguements (database_mode = 2)
    parser.add_argument('--database_host', action='store', dest='database_host',
                        help='MySQL database hostname '
                             '(Only required if --databasemode=2. '
                             'If unset user is prompted for choice.')
    parser.add_argument('--database_user', action='store', dest='database_user',
                        help='MySQL database username '
                             '(Only required if --databasemode=2. '
                             'If unset user is prompted for choice.')
    parser.add_argument('--database_pass', action='store', dest='database_pass',
                        help='MySQL database password '
                             '(Only required if --databasemode=2. '
                             'If unset user is prompted for choice.')
    parser.add_argument('--database_name', action='store', dest='database_name',
                        help='MySQL database name '
                             '(Only required if --databasemode=2. '
                             'If unset user is prompted for choice.')
    parser.add_argument('--calib-table', action='store', dest='calibtable',
                        help='APERO database table name suffix for the'
                             'calibration database (default is the APERO '
                             'profile name). If unset user is prompted for '
                             'choice.')
    parser.add_argument('--tellu-table', action='store', dest='tellutable',
                        help='APERO database table name suffix for the'
                             'telluric database (default is the APERO '
                             'profile name). If unset user is prompted for '
                             'choice.')
    parser.add_argument('--index-table', action='store', dest='indextable',
                        help='APERO database table name suffix for the'
                             'index database (default is the APERO '
                             'profile name).')
    parser.add_argument('--log-table', action='store', dest='logtable',
                        help='APERO database table name suffix for the'
                             'log database (default is the APERO '
                             'profile name).')
    parser.add_argument('--obj-table', action='store', dest='objtable',
                        help='APERO database table name suffix for the'
                             'object database (default is the APERO '
                             'profile name).')
    parser.add_argument('--lang-table', action='store', dest='langtable',
                        help='APERO database table name suffix for the'
                             'language database (default is the APERO '
                             'profile name).')
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


def validate():
    """
    Check whether users system satisfies all python module requirements

    :raises SystemExit: if modules are not correct
    :return: None
    """
    # python version check
    if sys.version_info.major < 3:
        print('\tFatal Error: Python 2 is not supported')
        sys.exit()
    # ------------------------------------------------------------------
    # load requirement files
    # ------------------------------------------------------------------
    filepath = os.path.abspath(__file__)
    # get files
    user_req_file = Path(filepath).parent.parent.joinpath(REQ_USER)
    dev_req_file = Path(filepath).parent.parent.joinpath(REQ_DEV)
    # get lists of modules
    user_req = load_requirements(user_req_file)
    dev_mode = [False] * len(user_req)
    dev_req = load_requirements(dev_req_file)
    dev_mode += [True] * len(dev_req)
    modules = user_req + dev_req
    # storage of checked modules
    checked = []
    # log check
    print('Module check:')
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
            emsgs = 'Module name "{0}" error {1}: {2}'
            eargs = [module, type(e), str(e)]
            raise IndexError(emsgs.format(*eargs))

        suggested = 'pip install {0}'.format(module)
        # deal with modules with different import name
        if modname in module_translation:
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
                          required=not dev_mode[m_it])
        # --------------------------------------------------------------
        except Exception as _:
            if dev_mode[m_it]:
                print('\t{0} recommends {1} to be installed (dev only)'
                      '\n\t i.e {2}'.format(DRS_PATH, module, suggested))
            else:
                print('\tFatal Error: {0} requires module {1} to be installed'
                      '\n\t i.e {2}'.format(DRS_PATH, module, suggested))
                sys.exit()


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
            print('\t{0} recommends {1} to be updated ({3} < {2})'
                  '\n\t i.e {4}'.format(*args))
        elif not passed:
            print('\tFatal Error: {0} requires module {1} ({3} < {2})'
                  '\n\t i.e {4}'.format(*args))
            sys.exit()
        else:
            print('\tPassed: {1} ({3} >= {2})'.format(*args))


def catch_sigint(signal_received: Any, frame: Any):
    """
    Deal with Keyboard interupt --> do a sys.exit

    :param signal_received: Any, not used (but expected)
    :param frame: Any, not used (but expected)

    :return: None, exits if this function is called
    """
    # we don't use these we just exit
    _ = signal_received, frame
    print('\n\nExiting installation script')
    # raise Keyboard Interrupt
    sys.exit()


def check_install() -> Tuple[Any, Any]:
    """
    Check for apero installation directory

    :raises ImportError: if unable to find apero installation
    :return: tuple, 1. the apero.constants sub-module, 2. the apero.installation
             module
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
        raise ImportError('Unable to find {0}'.format(path))
    # construct module names
    constants_mod = '{0}.{1}'.format(DRS_PATH, CONSTANTS_PATH)
    install_mod = '{0}.{1}'.format(DRS_PATH, INSTALL_PATH)
    # try to import the modules
    try:
        constants = importlib.import_module(constants_mod)
    except Exception as _:
        # raise error
        raise ImportError('Cannot import {0}'.format(constants_mod))
    try:
        install = importlib.import_module(install_mod)
    except Exception as _:
        # raise error
        raise ImportError('Cannot import {0}'.format(install_mod))
    # add apero to the PYTHONPATH
    if 'PYTHONPATH' in os.environ:
        oldpath = os.environ['PYTHONPATH']
        os.environ['PYTHONPATH'] = str(drs_path) + os.pathsep + oldpath
    # else we just add it to current PYTHON PATH
    else:
        os.environ['PYTHONPATH'] = str(drs_path)
        # add to active path
        os.sys.path = [str(drs_path)] + os.sys.path
    # if we have reached this point we can break out of the while loop
    return constants, install


def main():
    """
    Run the installation

    :return:
    """
    # ----------------------------------------------------------------------
    # get arguments
    args = get_args()
    # ----------------------------------------------------------------------
    # deal with validation
    if not args.skip:
        validate()
    # ----------------------------------------------------------------------
    # Importing DRS paths
    # ----------------------------------------------------------------------
    # catch Ctrl+C
    signal.signal(signal.SIGINT, catch_sigint)
    # get install paths
    constants, install = check_install()
    # noinspection PyBroadException
    try:
        from apero.tools.module.setup import drs_installation as install
        from apero.core import constants
    except Exception as _:
        pass
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
        print('GUI features not implemented yet.')
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
    install.cprint('Installing', 'm')
    install.cprint(install.printheader(), 'm')
    print('\n')
    # ----------------------------------------------------------------------
    # get binary paths
    install.cprint('\n- Getting binary paths', 'm')
    allparams = install.bin_paths(params, allparams)
    # ----------------------------------------------------------------------
    # copy config files to config dir
    install.cprint('\n- Creating config files', 'm')
    allparams = install.create_configs(params, allparams)
    # ----------------------------------------------------------------------
    # update config values from iparams
    install.cprint('\n- Updating config files', 'm')
    allparams = install.update_configs(allparams)
    # ----------------------------------------------------------------------
    # create source files to add environmental variables
    install.cprint('\n- Creating shell script(s)', 'm')
    allparams = install.create_shell_scripts(params, allparams)
    # ----------------------------------------------------------------------
    # perform clean install on each instrument if requested
    install.cprint('\n- Copying files\n\n', 'm')
    allparams = install.clean_install(params, allparams)
    # ----------------------------------------------------------------------
    # create sym links for all recipes
    install.cprint('\n- Creating symlinks\n', 'm')
    allparams = install.create_symlinks(params, allparams)
    # ----------------------------------------------------------------------
    # display message
    install.print_options(params, allparams)
    # ----------------------------------------------------------------------
    # log that installation is complete
    print('\n\n\n')
    install.cprint(install.printheader(), 'm')
    install.cprint('Installation complete', 'm')
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

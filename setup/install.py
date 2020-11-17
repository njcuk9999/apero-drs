#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-26 at 15:54

@author: cook
'''
import numpy as np
import importlib
import glob
import os
import sys
import signal
import argparse
from pathlib import Path

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
# set modules required
REQ_MODULES = dict()
REQ_MODULES['astropy'] = [4, 0, 0], 'conda install astropy==4.0'
REQ_MODULES['matplotlib'] = [3, 1, 2], 'conda install matplotlib==3.1.2'
REQ_MODULES['numpy'] = [1, 18, 1], 'conda install numpy==1.18.1'
REQ_MODULES['pandas'] = [0, 25, 3], 'conda install pandas==0.25.3'
REQ_MODULES['scipy'] = [1, 4, 1], 'conda install scipy==1.4.1'
REQ_MODULES['yaml'] = [5, 3, 1], 'conda install pyyaml==5.3.1'

REC_MODULES = dict()
REC_MODULES['astroquery'] = [0, 3, 10], 'pip install astroquery==0.3.10'
REC_MODULES['barycorrpy'] = [0, 3, 1], 'pip install barycorrpy=0.3.1'
REC_MODULES['bottleneck'] = [1, 3, 1], 'conda install bottleneck==1.3.1'
REC_MODULES['numba'] = [0, 47, 0], 'conda install numba==0.47.0'
REC_MODULES['PIL'] = [7, 0, 0], 'conda install Pillow==7.0.0'
REC_MODULES['tqdm'] = [4, 42, 1], 'conda install tdqm==4.42.1'
REC_MODULES['yagmail'] = [0, 11, 224], 'pip install yagmail==0.11.224'

DEV_MODULES = dict()
DEV_MODULES['gitchangelog'] = [3, 0, 4], 'pip install gitchangelog==3.0.4'
DEV_MODULES['ipdb'] = None, 'conda install ipdb'
DEV_MODULES['IPython'] = [7, 13, 0], 'conda install ipython==7.13.0'
DEV_MODULES['sphinx'] = [2, 3, 1], 'conda install sphinx==2.3.1'
DEV_MODULES['xlrd'] = [1, 2, 0], 'pip install xlrd==1.2.0'


# =============================================================================
# Define functions
# =============================================================================
def get_args():
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

    # add setup args
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
    parser.add_argument('--plotmode', action='store', dest='plotmode',
                        help='The plot mode. 0=Summary plots only '
                             '1=Plot at end of run 2=Plot at creation '
                             '(pauses code). If unset user is prompted for '
                             'choice.',
                        choices=['0', '1', '2'])
    parser.add_argument('--clean', action='store', dest='clean',
                        help='Whether to run from clean directories - '
                             'RECOMMENDED - clears out old files and copies'
                             'over all required default data files. '
                             'If unset user is prompted for  choice.')
    parser.add_argument('--clean_no_warning', action='store', dest='cleanwarn',
                        help='Whether to warn about cleaning populated '
                             'directories - WARNING if set to True will delete '
                             'all tmp/reduced/calibDB etc. data without prompt')
    parser.add_argument('--ds9path', action='store', dest='ds9path',
                        help='Optionally set the ds9 path (used in some tools)')
    parser.add_argument('--pdflatexpath', action='store', dest='pdfpath',
                        help='Optionally set the pdf latex path (used to '
                             'produce summary plots. '
                             'If unset user is prompted for choice.'
                             'If still unset user will only have html summary'
                             'document not a pdf one.')
    # parse arguments
    args = parser.parse_args()
    return args


def validate():
    # python version check
    if sys.version_info.major < 3:
        print('\tFatal Error: Python 2 is not supported')
        sys.exit()
    # log check
    print('Module check:')
    # ------------------------------------------------------------------
    # loop around required modules to check
    # ------------------------------------------------------------------
    for module in REQ_MODULES:
        # get required minimum version
        rversionlist = REQ_MODULES[module][0]
        suggested = REQ_MODULES[module][1]
        # ------------------------------------------------------------------
        # test importing module
        try:
            imod = importlib.import_module(module)
        except:
            print('\tFatal Error: {0} requires module {1} to be installed'
                  '\n\t i.e {2}'.format(DRS_PATH, module, suggested))
            sys.exit()
        # --------------------------------------------------------------
        # check the version
        check_version(module, imod, rversionlist, suggested, required=True)

    # ------------------------------------------------------------------
    # loop around recommended modules to check
    # ------------------------------------------------------------------
    for module in REC_MODULES:
        # get required minimum version
        rversionlist = REC_MODULES[module][0]
        suggested = REC_MODULES[module][1]
        # --------------------------------------------------------------
        # test importing module
        try:
            imod = importlib.import_module(module)
        except:
            print('\t{0} recommends {1} to be installed'
                  '\n\t i.e {2}'.format(DRS_PATH, module, suggested))
            continue
        # --------------------------------------------------------------
        # check the version
        check_version(module, imod, rversionlist, suggested, required=False)

    # ------------------------------------------------------------------
    # loop around devloper modules to check
    # ------------------------------------------------------------------
    for module in DEV_MODULES:
        # get required minimum version
        rversionlist = DEV_MODULES[module][0]
        suggested = DEV_MODULES[module][1]
        # --------------------------------------------------------------
        # test importing module
        try:
            imod = importlib.import_module(module)
        except:
            print('\t{0} recommends {1} to be installed (dev only)'
                  '\n\t i.e {2}'.format(DRS_PATH, module, suggested))
            continue
        # --------------------------------------------------------------
        # check the version
        check_version(module, imod, rversionlist, suggested, required=False)


def check_version(module, imod, rversionlist, suggested, required=True):
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
            # if we don't have a level this deep break
            if len(version) < (v_it - 1):
                break
            # try to make an integer
            try:
                version[v_it] = int(version[v_it])
            except:
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


def catch_sigint(signal_received, frame):
    print('\n\nExiting installation script')
    # raise Keyboard Interrupt
    sys.exit()


class PathCompleter(object):
    '''
    Copy of drs_installation.py.PathCompleter
    '''

    def __init__(self, root=None):
        self.root = root
        try:
            self.readline = importlib.import_module('readline')
        except:
            self.readline = None

    def pathcomplete(self, text, state):
        '''
        This is the tab completer for systems paths.
        Only tested on *nix systems
        '''
        line = self.readline.get_line_buffer().split()
        # replace ~ with the user's home dir.
        # See https://docs.python.org/2/library/os.path.html
        if '~' in text:
            text = os.path.expanduser('~')
        # deal with having a root folder
        if self.root is not None:
            text = os.path.join(self.root, text)
        # return list
        return [x for x in np.sort(glob.glob(text + '*'))][state]


def tab_input(message, root=None):
    '''
    copy of drs_installation.py.tab_input
    :param message:
    :param root:
    :return:
    '''
    # try to import readline (unix only)
    try:
        readline = importlib.import_module('readline')
    except:
        readline = None
    # deal with no readline module
    if readline is None:
        return input(message + '\n\t>> ')
    # ----------------------------------------------------------------------
    # Register our completer function
    readline.set_completer(PathCompleter(root).pathcomplete)
    # for MAC users
    if sys.platform == 'darwin':
        # Apple uses libedit.
        # readline.parse_and_bind('bind -e')
        # readline.parse_and_bind('bind '\t' rl_complete')
        pass
    # for everyone else
    elif sys.platform == 'linux':
        # Use the tab key for completion
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>?')
    uinput = input(message + '\n\t>> ')
    # return uinput
    return uinput


def check_install():
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
    except Exception as e:
        # raise error
        raise ImportError('Cannot import {0}'.format(constants_mod))
    try:
        install = importlib.import_module(install_mod)
    except Exception as e:
        # raise error
        raise ImportError('Cannot import {0}'.format(install_mod))

    # add apero to the PYTHONPATH
    if 'PYTHONPATH' in os.environ:
        oldpath = os.environ['PYTHONPATH']
        os.environ['PYTHONPATH'] = str(drs_path) + os.pathsep + oldpath

    else:
        os.environ['PYTHONPATH'] = str(drs_path)
        # add to active path
        os.sys.path = [str(drs_path)] + os.sys.path

    # if we have reached this point we can break out of the while loop
    return constants, install


def ask_for_install_path(drs_path: Path, debug):
    umsg = '\nCannot find {0}. Please enter {0} installation path:'
    # user input required
    uinput = tab_input(umsg.format(drs_path))
    # try to create path from user input
    try:
        upath = Path(uinput)
        # make sure user input exists
        if not upath.exists():
            umsg = ('\nPath "{0}" does not exist.'
                    '\nPlease enter a valid path. (Ctrl+C) to quit')
            print(umsg.format(upath))
        # if it does exist add it as a path to test
        else:
            # add debug output
            if debug:
                print('Adding "{0}" to sys.path'.format(upath))
            # update
            sys.path.append(upath)
    except:
        umsg = ('\nPath "{0}" is not a valid path.'
                '\nPlease enter a valid path. (Ctrl+C) to quit')
        print(umsg.format(uinput))


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == '__main__':
    # get arguments
    args = get_args()

    # deal with validation
    if not args.skip:
        validate()

    # ----------------------------------------------------------------------
    # Importing DRS paths
    # ----------------------------------------------------------------------
    # set guess path
    drs_path = Path(DRS_PATH)
    # catch Ctrl+C
    signal.signal(signal.SIGINT, catch_sigint)
    # get install paths
    constants, install = check_install()
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
        allparams = install.user_interface(params, args, LANGUAGE)
    else:
        allparams = install.update(params, args)
    # add dev mode to allparams
    allparams['DEVMODE'] = args.devmode
    # add name
    allparams['PROFILENAME'] = args.name
    # add clean warn
    allparams['CLEANWARN'] = args.cleanwarn
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
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-26 at 15:54

@author: cook
"""
import importlib
import glob
import os
import sys
import signal

# =============================================================================
# Define variables
# =============================================================================
# define the drs name (and module name)
DRS_PATH = 'apero'
# define the place where the constant recipes are
CONSTANTS_PATH = 'core.constants'
# define the place where the installation recipes are
INSTALL_PATH = 'tools.module.setup.drs_installation'
# set modules required
REQ_MODULES = dict()
REQ_MODULES['astropy'] = [2, 0, 3]
REQ_MODULES['matplotlib'] = [2, 1, 2]
REQ_MODULES['numpy'] = [1, 14, 0]
REQ_MODULES['scipy'] = [1, 0, 0]
REC_MODULES = dict()
REC_MODULES['astroquery'] = [0, 3, 9]
REC_MODULES['barycorrpy'] = [0, 2, 2, 1]
REC_MODULES['bottleneck'] = [1, 2, 1]
REC_MODULES['ipdb'] = None
REC_MODULES['numba'] = [0, 41, 0]
REC_MODULES['pandas'] = [0, 23, 4]
REC_MODULES['PIL'] = [5, 3, 0]
REC_MODULES['tqdm'] = [4, 28, 1]
REC_MODULES['yagmail'] = [0, 11, 220]
# the help message
HELP_MESSAGE = """
 ***************************************************************************
 Help for: 'setup/install.py'
 ***************************************************************************
	NAME: setup/install.py
	AUTHORS: N. Cook, E. Artigau, F. Bouchy, M. Hobson, C. Moutou, 
	         I. Boisse, E. Martioli

 Usage: install.p [options]


 ***************************************************************************
 Description:
 ***************************************************************************

 Install {0} software for reducing observational data
 
 ***************************************************************************

Optional Arguments:

--gui          use GUI to install (Not yet supported)  

--skip         skip the python module checks (Not recommended)

--dev          activate developer mode (adds all constants to user config/
               constant files

--update       updates installation (not clean install)

--help, -h     show this help message and exit

 ***************************************************************************

"""


# =============================================================================
# Define functions
# =============================================================================
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
        rversionlist = REQ_MODULES[module]
        # ------------------------------------------------------------------
        # test importing module
        try:
            imod = importlib.import_module(module)
        except:
            print('\tFatal Error: {0} requires module {1} to be installed'
                  ''.format(DRS_PATH, module))
            sys.exit()
        # --------------------------------------------------------------
        # check the version
        check_version(module, imod, rversionlist, required=True)

    # ------------------------------------------------------------------
    # loop around required modules to check
    # ------------------------------------------------------------------
    for module in REC_MODULES:
        # get required minimum version
        rversionlist = REC_MODULES[module]
        # --------------------------------------------------------------
        # test importing module
        try:
            imod = importlib.import_module(module)
        except:
            print('\t{0} recommends {1} to be installed'
                  ''.format(DRS_PATH, module))
            continue
        # --------------------------------------------------------------
        # check the version
        check_version(module, imod, rversionlist, required=False)


def check_version(module, imod, rversionlist, required=True):
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
        args = [DRS_PATH, module, '.'.join(rstrlist), '.'.join(strlist)]
        # if we have not passed print fail message
        if not passed and not required:
            print('\t{0} recommends {1} to be updated ({3} < {2})'
                  ''.format(*args))
        elif not passed:
            print('\tFatal Error: {0} requires module {1} ({3} < {2})'
                  ''.format(*args))
            sys.exit()
        else:
            print('\tPassed: {1} ({3} >= {2})'.format(*args))


def catch_sigint(signal_received, frame):
    print('\n\nExiting installation script')
    # raise Keyboard Interrupt
    sys.exit()


class PathCompleter(object):
    """
    Copy of drs_installation.py.PathCompleter
    """
    def __init__(self, root=None):
        self.root = root
        try:
            self.readline = importlib.import_module('readline')
        except:
            self.readline = None

    def pathcomplete(self, text, state):
        """
        This is the tab completer for systems paths.
        Only tested on *nix systems
        """
        line = self.readline.get_line_buffer().split()
        # replace ~ with the user's home dir.
        # See https://docs.python.org/2/library/os.path.html
        if '~' in text:
            text = os.path.expanduser('~')
        # deal with having a root folder
        if self.root is not None:
            text = os.path.join(self.root, text)
        # return list
        return [x for x in glob.glob(text + '*')][state]


def tab_input(message, root=None):
    """
    copy of drs_installation.py.tab_input
    :param message:
    :param root:
    :return:
    """
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
        # readline.parse_and_bind("bind -e")
        # readline.parse_and_bind("bind '\t' rl_complete")
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
    # loop until we can import modules
    while cond:
        # try to import the drs
        try:
            drs = importlib.import_module(drs_path)
        except Exception as _:
            umsg = '\nCannot find {0}. Please enter {0} installation path:'
            # user input required
            uinput = tab_input(umsg.format(drs_path))
            # make sure user input exists
            if not os.path.exists(uinput):
                umsg = ('\nPath "{0}" does not exist.'
                        '\nPlease enter a valid path. (Ctrl+C) to quit')
                print(umsg.format(uinput))
            else:
                sys.path.append(uinput)
            continue
        # construct module names
        constants_mod = '{0}.{1}'.format(drs_path, CONSTANTS_PATH)
        install_mod = '{0}.{1}'.format(drs_path, INSTALL_PATH)
        # try to import the modules
        try:
            print('Loading {0}'.format(constants_mod))
            constants = importlib.import_module(constants_mod)
        except Exception as _:
            print('Cannot import {0}. Exiting'.format(constants_mod))
            sys.exit()
        try:
            print('Loading {0}'.format(install_mod))
            install = importlib.import_module(install_mod)
        except Exception as _:
            print('Cannot import {0}. Exiting'.format(install_mod))
            sys.exit()

        # add apero to the PYTHONPATH
        if 'PYTHONPATH' in os.environ:
            oldpath = os.environ['PYTHONPATH']
            os.environ['PYTHONPATH'] = drs_path + os.pathsep + oldpath
        else:
            os.environ['PYTHONPATH'] = drs_path
        # add to active path
        os.sys.path = [drs_path] + os.sys.path

        # if we have reached this point we can break out of the while loop
        return constants, install, drs_path



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":


    # get arguments
    args = sys.argv
    # ----------------------------------------------------------------------
    # Help
    if '--help' in args or '-h' in args:
        print(HELP_MESSAGE.format(DRS_PATH))
        sys.exit()
    # Validate modules
    if '--skip' not in args:
        validate()
    # Dev mode
    if '--dev' in args:
        devmode = True
    else:
        devmode = False
    # Update mode
    if '--update' in args:
        update = True
    else:
        update = False

    # ----------------------------------------------------------------------
    # Importing DRS paths
    # ----------------------------------------------------------------------
    # set import condition to True
    cond = True
    # set guess path
    drs_path = str(DRS_PATH)
    # catch Ctrl+C
    signal.signal(signal.SIGINT, catch_sigint)
    # get install paths
    constants, install, root = check_install()

    # ----------------------------------------------------------------------
    # start up
    # ----------------------------------------------------------------------
    # get global parameters
    params = constants.load()

    # ----------------------------------------------------------------------
    # Start of user setup
    # ----------------------------------------------------------------------
    # if gui pass for now
    if '--gui' in args:
        print('GUI features not implemented yet.')
        sys.exit()
    # get parameters from user input
    elif not update:
        allparams = install.user_interface(params)
    else:
        allparams = install.update(params)
    # add root to allparams
    allparams['ROOT'] = root

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
    install.cprint('\n- Copying config files', 'm')
    allparams = install.copy_configs(params, allparams)
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

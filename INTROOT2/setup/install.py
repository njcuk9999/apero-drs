#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-26 at 15:54

@author: cook
"""
import importlib
import readline
import glob
import os
import sys
from signal import signal, SIGINT


# =============================================================================
# Define variables
# =============================================================================
# define the drs name (and module name)
DRS_PATH = 'terrapipe'
# define the place where the constant recipes are
CONSTANTS_PATH = 'core.constants'
# define the place where the installation recipes are
INSTALL_PATH = 'tools.module.setup.drs_installation'

# =============================================================================
# Define functions
# =============================================================================
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

    def pathcomplete(self, text, state):
        """
        This is the tab completer for systems paths.
        Only tested on *nix systems
        """
        line = readline.get_line_buffer().split()

        # replace ~ with the user's home dir.
        # See https://docs.python.org/2/library/os.path.html
        if '~' in text:
            text = os.path.expanduser('~')

        # deal with having a root folder
        if self.root is not None:
            text = os.path.join(self.root, text)

        return [x for x in glob.glob(text + '*')][state]


def tab_input(message, root=None):
    """
    copy of drs_installation.py.tab_input
    :param message:
    :param root:
    :return:
    """
    # Register our completer function
    readline.set_completer(PathCompleter(root).pathcomplete)
    # for MAC users
    if sys.platform == 'darwin':
        # Apple uses libedit.
        readline.parse_and_bind("bind -e")
        readline.parse_and_bind("bind '\t' rl_complete")
    # for everyone else
    elif sys.platform == 'linux':
        # Use the tab key for completion
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>?')
    uinput = input(message + '\n\t>> ')
    # return uinput
    return uinput


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Importing DRS paths
    # ----------------------------------------------------------------------
    # set import condition to True
    cond = True
    # set guess path
    drs_path = str(DRS_PATH)
    # set modules to None
    constants, install = None, None
    # catch Ctrl+C
    signal(SIGINT, catch_sigint)
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
        # if we have reached this point we can break out of the while loop
        break

    # ----------------------------------------------------------------------
    # start up
    # ----------------------------------------------------------------------
    # get arguments
    args = sys.argv
    # get global parameters
    params = constants.load()

    # ----------------------------------------------------------------------
    # Start of user setup
    # ----------------------------------------------------------------------
    # if gui pass for now
    if '--gui' in args:
        print('GUI features not implemented yet.')
        sys.exit()
    else:
        allparams = install.user_interface(params)
    # ----------------------------------------------------------------------
    # End of user setup
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Installation
    # ----------------------------------------------------------------------
    # print installing title
    print('\n\n\n')
    install.cprint('=' * 50, 'm')
    install.cprint('Installing', 'm')
    install.cprint('=' * 50, 'm')
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
    # everything should now be set up - time to validate installation
    install.cprint('\n- Validating installation\n\n', 'm')
    allparams = install.validate_install(allparams)
    # ----------------------------------------------------------------------
    # perform clean install on each instrument if requested
    install.cprint('\n- Copying files\n\n', 'm')
    allparams = install.clean_install(allparams)
    # ----------------------------------------------------------------------
    # log that installation is complete
    print('\n\n\n')
    install.cprint('=' * 50, 'm')
    install.cprint('Installation complete', 'm')
    install.cprint('=' * 50, 'm')
    print('\n')

# =============================================================================
# End of code
# =============================================================================

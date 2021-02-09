#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-26 at 15:54

@author: cook
'''
import numpy as np
import argparse
import os
import glob
import sys
import signal
import shutil
from pathlib import Path

from apero.base import base
from apero.core import constants
from apero.tools.module.setup import drs_installation as install
from apero.io import drs_path

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'setup.newprofile.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# define the drs name (and module name)
DRS_PATH = 'apero'
# define the place where the constant recipes are
CONSTANTS_PATH = 'core.constants'
# define the place where the installation recipes are
INSTALL_PATH = 'tools.module.setup.drs_installation'
# define files to change the name of
SUFFICES = ['.bash.setup', '.sh.setup']
# text replace
OLDTEXT = '" ${YELLOW}}'

TEXTCHANGE = ['${{yellow}}{PROFILENAME}', '${{YELLOW}}{PROFILENAME}',
              '{UCONFIG}']

# =============================================================================
# Define functions
# =============================================================================
def catch_sigint(signal_received, frame):
    print('\n\nExiting installation script')
    # raise Keyboard Interrupt
    sys.exit()


def get_args():
    # get parser
    description = ' Install {0} software for reducing observational data'
    parser = argparse.ArgumentParser(description=description.format(DRS_PATH))
    parser.add_argument('--name', action='store', dest='name',
                        help='The name of the new APERO profile')
    parser.add_argument('--path', action='store', dest='path',
                        help='The path to install new APERO profile to '
                             '(If unset uses old profile path)')
    parser.add_argument('--debug', action='store', dest='debug',
                        help='Run installer in debug mode')
    parser.add_argument('--clean', action='store', dest='clean',
                        help='Whether to run from clean directories - '
                             'RECOMMENDED - clears out old files and copies'
                             'over all required default data files. '
                             'If unset user is prompted for  choice.')
    # parse arguments
    args = parser.parse_args()
    # need fake clean argument
    args.clean = False
    # return arguments
    return args


def old_new(args, all_params):
    if args.name is None:
        name = install.ask('Define a name for new profile', dtype=str)
    else:
        name = args.name
    # clean name
    name = name.strip().replace(' ', '_')
    all_params['PROFILENAME'] = name
    # ----------------------------------------------------------------------
    # previous user config
    # ----------------------------------------------------------------------
    old_user_config = Path(all_params['USERCONFIG'])
    all_params['OLD_USERCONFIG'] = old_user_config
    # ----------------------------------------------------------------------
    # get the path
    # ----------------------------------------------------------------------
    # assume directory is changed to name
    if args.path is None:
        # just in case user gave us a file
        if old_user_config.is_file():
            user_path = old_user_config.parent.parent
        else:
            user_path = old_user_config.parent
    else:
        user_path = Path(args.path)
    # check path exists
    if not user_path.exists():
        install.cprint('Error: Path invalid. \n\t Path = {0}'.format(user_path))
        sys.exit()

    # create new path
    new_path = user_path.joinpath(name)
    all_params['USERCONFIG'] = new_path
    # ----------------------------------------------------------------------
    # create new path
    # ----------------------------------------------------------------------
    if new_path.exists():
        install.cprint('Error: Path exists. \n\t Path = {0}'.format(new_path))
        sys.exit()
    else:
        new_path.mkdir()

    # return all params
    return all_params


def copy_update(all_params):

    old_uconfig = all_params['OLD_USERCONFIG']
    new_path = all_params['USERCONFIG']
    profilename = all_params['PROFILENAME']
    # ----------------------------------------------------------------------
    # find special files
    # ----------------------------------------------------------------------
    all_old_files = np.sort(list(old_uconfig.glob('*')))
    old_profile_name = ''
    old_setup_files = []
    new_setup_files = []
    old_other_files = []
    new_other_files = []
    # loop around these files
    for old_file in all_old_files:
        # set default old_file and new file
        new_abspath = Path(new_path).joinpath(old_file.name)
        # deal with setup files vs other files
        setup_file = False
        # loop around suffices
        for suffix in SUFFICES:
            # check for suffix
            if str(old_file).endswith(suffix):
                # get old file suffix
                old_path = Path(str(old_file).split(suffix)[0])
                old_profile_name = old_path.name
                # construct new file
                new_file = '{0}{1}'.format(profilename, suffix)
                new_abspath = Path(new_path).joinpath(new_file)
                setup_file = True
                break
        # add to setup files or other files
        if setup_file:
            old_setup_files.append(old_file)
            new_setup_files.append(new_abspath)
        else:
            old_other_files.append(old_file)
            new_other_files.append(new_abspath)

    # ----------------------------------------------------------------------
    # set old and new text dicts
    # ----------------------------------------------------------------------
    OLDDICT = dict(PROFILENAME=old_profile_name, UCONFIG=old_uconfig)
    NEWDICT = dict(PROFILENAME=profilename, UCONFIG=new_path)

    # ----------------------------------------------------------------------
    # copy all to new path
    # ----------------------------------------------------------------------
    # copy other files
    for it in range(len(old_other_files)):
        install.cprint('Copying file: {0}'.format(old_other_files[it]), 'g')
        install.cprint('To: {0}'.format(new_other_files[it]), 'g')
        # make new top level dir
        shutil.copy(old_other_files[it], new_other_files[it])
    # need to update setup files
    for it in range(len(old_setup_files)):

        install.cprint('Copying file: {0}'.format(old_setup_files[it]), 'g')
        install.cprint('To: {0}'.format(new_setup_files[it]), 'g')
        # read the lines
        with old_setup_files[it].open('r') as f:
            lines = f.readlines()
        # storage new line text
        newlines = []
        # loop around lines
        for line in lines:
            # loop around text
            for text in TEXTCHANGE:
                oldtext = text.format(**OLDDICT)
                newtext = text.format(**NEWDICT)
                if oldtext in line:
                    msg = '\tReplacing text: {0} --> {1}'
                    install.cprint(msg.format(oldtext, newtext), 'g')
                    line = line.replace(oldtext, newtext)
            # add line to newlines
            newlines.append(line)
        # write the lines
        with new_setup_files[it].open('w') as f:
            f.writelines(newlines)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == '__main__':
    # set up arguments
    args = get_args()
    # catch Ctrl+C
    signal.signal(signal.SIGINT, catch_sigint)
    # ----------------------------------------------------------------------
    # start up
    # ----------------------------------------------------------------------
    # get global parameters
    params = constants.load(from_file=False)
    # get all params
    # TODO: outpaths for setup files are not correct (missing directory)
    allparams = install.update(params, args)
    # ----------------------------------------------------------------------
    # get old and new parameters
    # ----------------------------------------------------------------------
    allparams = old_new(args, allparams)
    # ----------------------------------------------------------------------
    # copy files and update
    # ----------------------------------------------------------------------
    copy_update(allparams)
    # ----------------------------------------------------------------------
    # display message
    install.print_options(params, allparams)
    # ----------------------------------------------------------------------
    # log extra message for new profile
    msg = ('\n\nIMPORTANT: This script copies all parameters for the currently '
           'loaded APERO profile:\n\t{0}\n\n You must review and update all '
           'files manually at the following path before running APERO:'
           '\n\t{1}\n\nNote this includes creating new directories and running'
           'apero_reset.py once all directories are added to the new config '
           'files.')
    margs = [allparams['OLD_USERCONFIG'], allparams['USERCONFIG']]
    install.cprint(msg.format(*margs), 'y')
    # ----------------------------------------------------------------------
    # log that installation is complete
    print('\n\n\n')
    install.cprint(install.printheader(), 'm')
    install.cprint('New profile setup complete', 'm')
    install.cprint(install.printheader(), 'm')
    print('\n')


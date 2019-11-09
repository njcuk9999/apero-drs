#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-09 10:44
@author: ncook
Version 0.0.1
"""
import numpy as np
import sys
import os
import shutil
import glob

from terrapipe.core import constants
from terrapipe.core.instruments.default import pseudo_const
from terrapipe.locale import drs_exceptions


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_installation.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']

# get colors
Colors = pseudo_const.Colors()
# get param dict
ParamDict = constants.ParamDict
# get the Drs Exceptions
DRSError = drs_exceptions.DrsError
DRSWarning = drs_exceptions.DrsWarning
TextError = drs_exceptions.TextError
TextWarning = drs_exceptions.TextWarning
ConfigError = drs_exceptions.ConfigError
ConfigWarning = drs_exceptions.ConfigWarning
# -----------------------------------------------------------------------------
INSTRUMENTS = ['SPIROU', 'NIRPS']
DEFAULT_USER_PATH = '~/terrapipe/config/'
DEFAULT_DATA_PATH = '~/terrapipe/data/'
DATA_PATHS = dict()
DATA_PATHS['DRS_DATA_RAW'] = ['Raw data directory', 'raw']
DATA_PATHS['DRS_DATA_WORKING'] = ['Temporary data directory', 'tmp']
DATA_PATHS['DRS_DATA_REDUC'] = ['Reduced data directory', 'reduced']
DATA_PATHS['DRS_CALIB_DB'] = ['Calibration DB data directory', 'calibDB']
DATA_PATHS['DRS_TELLU_DB'] = ['Telluric DB data directory', 'telluDB']
DATA_PATHS['DRS_DATA_PLOT'] = ['Plotting directory', 'plot']
DATA_PATHS['DRS_DATA_RUN'] = ['Run directory', 'runs']
DATA_PATHS['DRS_DATA_MSG'] = ['Log directory', 'msg']


# =============================================================================
# Define functions
# =============================================================================
def cprint(message, colour='g'):
    """
    print coloured message

    :param message: str, message to print
    :param colour: str, colour to print
    :return:
    """
    print(Colors.print(message, colour))


def ask(question, dtype=None, options=None, optiondesc=None, default=None):
    """
    Ask a question

    :param question: str, the question to ask
    :param dtype: str, the data type (int/float/bool/str/path/YN)
    :param options: list, list of valid options
    :param optiondesc: list, list of option descriptions
    :param default: object, if set the default value, if unset a value
                    if required
    :return:
    """
    # set up check criteria as True at first
    check = True
    # set up user input as unset
    uinput = None
    # deal with yes/no dtype
    if isinstance(dtype, str) and dtype.upper() == 'YN':
        options = ['Y', 'N']
        optiondesc = ['[Y]es or [N]o']
    # loop around until check is passed
    while check:
        # ask question
        cprint(question, 'g')
        # print options
        if options is not None:
            cprint('Options are:', 'b')
            print('\t' + '\n\t'.join(np.array(optiondesc, dtype=str)))
        if default is not None:
            cprint('\tDefault is: {0}'.format(default), 'b')
        # record responce
        uinput = input(' >>\t')
        # deal with ints, floats, logic
        if dtype in ['int', 'float', 'bool']:
            try:
                basetype = eval(dtype)
                uinput = basetype(uinput)
                check = False
            except Exception as _:
                if uinput == '' and default is not None:
                    check = False
                else:
                    cprint('Response must be valid {0}'.format(dtype), 'y')
                    check = True
                    continue
        # deal with paths
        elif dtype == 'path':
            # check whether default wanted
            if uinput == '' and default is not None:
                uinput = default
            elif uinput == '':
                cprint('Response invalid', 'y')
                check = True
                continue
            # get rid of expansions
            uinput = os.path.expanduser(uinput)
            # check whether path exists
            if os.path.exists(uinput):
                check = False
            # if path does not exist ask to make it (if create)
            else:
                # check whether to create path
                pathquestion = 'Path "{0}" does not exist. Create?'
                create = ask(pathquestion.format(uinput), dtype='YN')
                if create:
                    if not os.path.exists(uinput):
                        os.makedirs(uinput)
                    check = False
                    continue
                else:
                    cprint('Response must be a valid path', 'y')
                    check = True
                    continue
        # deal with Yes/No questions
        elif dtype == 'YN':
            if 'Y' in uinput:
                return True
            elif 'N' in uinput:
                return False
            else:
                cprint('Response must be [Y]es or [N]o', 'y')
                check = True
                continue
        # deal with everything else
        else:
            pass
        # deal with options
        if options is not None:
            # convert options to string
            options = np.char.array(np.array(options, dtype=str))
            if str(uinput).upper() in options.upper():
                check = False
                continue
            elif uinput == '' and default is not None:
                check = False
                continue
            else:
                optionstr = ' or '.join(np.array(options, dtype=str))
                cprint('Response must be {0}'.format(optionstr), 'y')
                check = True
    # deal with returning default
    if uinput == '' and default is not None:
        return default
    else:
        # return uinput
        return uinput


def user_interface(params):

    # get default from params
    package = params['DRS_PACKAGE']
    # storage of answers
    all_params = dict()
    # title
    cprint('=' * 50, 'm')
    cprint('Installation for {0}'.format(package), 'm')
    cprint('=' * 50, 'm')
    print('\n')

    # ------------------------------------------------------------------
    # Step 1: Ask for user config path
    userconfig = ask('User config path', 'path', default=DEFAULT_USER_PATH)
    all_params['userconfig'] = userconfig
    # ------------------------------------------------------------------
    for instrument in INSTRUMENTS:
        # ------------------------------------------------------------------
        cprint('\n' + '=' * 50, 'm')
        cprint('Settings for {0}'.format(instrument), 'm')
        cprint('=' * 50, 'm')
        # ------------------------------------------------------------------
        # set up blank dictionary
        iparams = ParamDict()
        # ------------------------------------------------------------------
        # Step 2: Ask for instruments to install
        install = ask('Install {0}?'.format(instrument), dtype='YN')
        if not install:
            continue
        cprint('=' * 50, 'g')
        # ------------------------------------------------------------------
        # set user config
        iparams['userconfig'] = os.path.join(userconfig, instrument.lower())
        # make instrument user config directory
        if not os.path.exists(iparams['userconfig']):
            os.mkdir(iparams['userconfig'])
        # ------------------------------------------------------------------
        # Step 3: Ask for data paths
        advanced = ask('Setup paths invidiually?', dtype='YN')
        cprint('=' * 50, 'g')
        # ------------------------------------------------------------------
        # if advanced then loop through all options
        if advanced:
            # loop around paths
            for path in DATA_PATHS:
                # get question and default
                question, default = DATA_PATHS[path]
                defaultpath = os.path.join(DEFAULT_DATA_PATH, default)
                # ask question and assign path
                iparams[path] = ask(question, 'path', default=defaultpath)
                iparams.set_source(path, __NAME__)
                cprint('=' * 50, 'g')
        # ------------------------------------------------------------------
        else:
            directory = ask('Data directory', 'path', default=DEFAULT_DATA_PATH)

            created = False
            # loop around paths
            for path in DATA_PATHS:
                # get question and default
                question, default = DATA_PATHS[path]
                # assign path
                iparams[path] = os.path.join(directory, default)
                iparams.set_source(path, __NAME__)
                # check whether path exists
                if not os.path.exists(iparams[path]):
                    pathquestion = 'Path "{0}" does not exist. Create?'
                    create = ask(pathquestion.format(iparams[path]), dtype='YN')
                    if create:
                        if not os.path.exists(iparams[path]):
                            os.makedirs(iparams[path])
                        cprint('=' * 50, 'g')
                        created = True
            if not created:
                cprint('=' * 50, 'g')
        # ------------------------------------------------------------------
        # Step 4: Ask for plot mode
        plot = ask('Plot mode required', dtype='int', options=[0, 1, 2],
                   optiondesc=['0: No plotting',
                               '1: Plots display at end of code',
                               '2: Plots display immediately and pause code'],
                   default=0)
        iparams['DRS_PLOT'] = plot
        iparams.set_source('DRS_PLOT', __NAME__)
        # ------------------------------------------------------------------
        # Step 5: Ask whether we want a clean install
        iparams['CLEAN_INSTALL'] = ask('Clean install?', dtype='YN')
        # ------------------------------------------------------------------
        # add iparams to all params
        all_params[instrument] = iparams

    cprint('=' * 50, 'm')
    # ----------------------------------------------------------------------
    # return all parameters
    return all_params


def copy_configs(params, all_params):
    # loop around instruments
    for instrument in INSTRUMENTS:
        # only deal with instrument user wants to set up
        if instrument not in list(all_params.keys()):
            continue
        # get iparams
        iparams = all_params[instrument]
        # get properties from iparams
        duser_config = params['DRS_USER_DEFAULT']
        package = params['DRS_PACKAGE']
        # get installation root
        iparams['DRS_ROOT'] = constants.get_relative_folder(package, '')
        # get config path
        configpath = constants.get_relative_folder(package, duser_config)
        # get instrument config path
        diconfigpath = os.path.join(configpath, instrument.lower())
        # get filelist
        files = glob.glob(diconfigpath + '/*')
        newfiles = []
        # get new config path
        userconfig = iparams['USERCONFIG']
        # copy contents of diconfigpath to userconfig
        for filename in files:
            # get new file location
            newpath = os.path.join(userconfig, os.path.basename(filename))
            # copy file from old to new
            if not os.path.exists(newpath):
                shutil.copy(filename, newpath)
            # store new config file locations
            newfiles.append(newpath)
        # store filenames in iparams
        iparams['CONFIGFILES'] = newfiles
    # return all_params
    return all_params


def update_configs(all_params):
    # loop around instruments
    for instrument in INSTRUMENTS:
        # only deal with instrument user wants to set up
        if instrument not in list(all_params.keys()):
            continue
        # get iparams
        iparams = all_params[instrument]
        # loop around config files
        for filename in iparams['CONFIGFILES']:
            # get the current config values
            fkeys, fvalues = constants.get_constants_from_file(filename)
            fdict = dict(zip(fkeys, fvalues))
            # loop around keys
            for key in fkeys:
                # test if key is new
                if (key in iparams) and (str(iparams[key]) != fdict[key]):
                    # update value
                    fdict[key] = iparams[key]
            # now update config file
            try:
                constants.update_file(filename, fdict)
            except ConfigError as e:
                emsg = 'Cannot update file. Error was as follows: \n\t{0}'
                print(emsg.format(e))
    return all_params


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get arguments
    args = sys.argv
    # get global parameters
    params = constants.load()
    # ----------------------------------------------------------------------
    # if gui pass for now
    if '--gui' in args:
        raise NotImplementedError('GUI features not implemented yet.')
    else:
        allparams = user_interface(params)
    # ----------------------------------------------------------------------
    # TODO: need to update DRS_UCONFIG environmental variable

    # ----------------------------------------------------------------------
    # copy config files to config dir
    allparams = copy_configs(params, allparams)
    # ----------------------------------------------------------------------
    # update config values from iparams
    allparams = update_configs(allparams)
    # ----------------------------------------------------------------------
    # copy initial files to drs (and prompt if not empty)




# =============================================================================
# End of code
# =============================================================================
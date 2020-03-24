#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-09 10:44
@author: ncook
Version 0.0.1
"""
import importlib
import numpy as np
import sys
import os
import shutil
import readline
import glob
from collections import OrderedDict

from apero.core import constants
from apero.core.instruments.default import pseudo_const
from apero.locale import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_installation.py'
__INSTRUMENT__ = 'None'
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
HOME = os.path.expanduser('~')
DEFAULT_USER_PATH = os.path.join(HOME, 'apero', 'default')
DEFAULT_DATA_PATH = os.path.join(HOME, 'apero', 'data', 'default')

UCONFIG = 'user_config.ini'
UCONST = 'user_constants.ini'

OUT_BINPATH = os.path.join('..', 'bin')
OUT_TOOLPATH = os.path.join('..', 'tools')

IN_BINPATH = os.path.join('.', 'recipes', '{0}', '')
IN_TOOLPATH = os.path.join('..', 'apero', 'tools', 'recipes')

ENV_CONFIG = 'DRS_UCONFIG'
SETUP_PATH = os.path.join('.', 'tools', 'resources', 'setup')

VALIDATE_CODE = os.path.join('bin', 'apero_validate.py')
RESET_CODE = 'apero_reset'
# set descriptions for data paths
# TODO: these should be in the constants file?
DATA_PATHS = dict()
DATA_PATHS['DRS_DATA_RAW'] = ['Raw data directory', 'raw']
DATA_PATHS['DRS_DATA_WORKING'] = ['Temporary data directory', 'tmp']
DATA_PATHS['DRS_DATA_REDUC'] = ['Reduced data directory', 'reduced']
DATA_PATHS['DRS_CALIB_DB'] = ['Calibration DB data directory', 'calibDB']
DATA_PATHS['DRS_TELLU_DB'] = ['Telluric DB data directory', 'telluDB']
DATA_PATHS['DRS_DATA_PLOT'] = ['Plotting directory', 'plot']
DATA_PATHS['DRS_DATA_RUN'] = ['Run directory', 'runs']
DATA_PATHS['DRS_DATA_MSG'] = ['Log directory', 'msg']
# set the reset paths (must be checked for empty)
RESET_PATHS = ['DRS_CALIB_DB', 'DRS_TELLU_DB', 'DRS_DATA_RUN']
# set cmdline args expected for each
DATA_ARGS = dict()
DATA_ARGS['DRS_DATA_RAW'] = 'rawdir'
DATA_ARGS['DRS_DATA_WORKING'] = 'tmpdir'
DATA_ARGS['DRS_DATA_REDUC'] = 'reddir'
DATA_ARGS['DRS_CALIB_DB'] = 'calibdir'
DATA_ARGS['DRS_TELLU_DB'] = 'telludir'
DATA_ARGS['DRS_DATA_PLOT'] = 'plotdir'
DATA_ARGS['DRS_DATA_RUN'] = 'rundir'
DATA_ARGS['DRS_DATA_MSG'] = 'logdir'

# Messages for user interface
message1 = """
User config path: 

    This is the path where your user configuration will be saved.
    If it doesn't exist you will be prompted to create it. 
    
    Note if creating multiple profiles (with --name) this should not be
    the same directory for each profile (must be different).
"""

message2 = """
Setup paths invidiually? [Y]es or [N]o
    
    If [Y]es it will allow you to set each path separately
    (i.e. for raw, tmp, reduced, calibDB etc). 
    If [N]o you will just set one path and all folders 
    (raw, tmp, reduced, calibDB etc) will be created under this 
    directory.
"""

message3 = """
Clean install? [Y]es or [N]o

    WARNING: If you type [Y]es you will be prompted (later) to reset
    the directories this means any previous data in these directories 
    will be removed.
    
Note you can always say later to individual cases.

Note if you have given empty directories you MUST run a clean install to copy
the required files to the given directories.
"""

message4 = """

    i) Add an alias in your ~/.bashrc or ~/.bash_profile or 
       ~/.tcshrc or ~/.profile 
       and then type "{NAME}" every time you wish to run apero.
       i.e. for bash
            alias {NAME}="source {DRS_UCONFIG}{NAME}.bash.setup"
       i.e. for sh
            alias {NAME} "source {DRS_UCONFIG}{NAME}.sh.setup"
    
    
    ii) Add the contents of {DRS_UCONFIG}{NAME}.{SYSTEM}.setup 
        to your ~/.bashrc or ~/.bash_profile or ~/.tcshrc or ~/.profile
    

    iii) type "source {DRS_UCONFIG}{NAME}.{SYSTEM}.setup" every 
         time you wish to run apero.
           i.e. for bash
                source {DRS_UCONFIG}{NAME}.bash.setup
           i.e. for sh
                source {DRS_UCONFIG}{NAME}.sh.setup


Note: here {SYSTEM} is "bash" or "sh" or "win" depending on your system.


"""

message5 = """

ds9 not found (optional). 

Please enter path to ds9 or leave blank to skip

"""

message6 = """

pdflatex not found (optional). 

Please enter path to pdflatex or leave blank to skip

"""


prompt1 = r"""

# =======================
# COLOURED PROMPT
# =======================
RED="\e[1;31m"
BLUE="\e[1;34m"
YELLOW="\e[0;33m"
WHITE="\e[0;37m"
END="\e[m"
export PS1=" ${YELLOW}{NAME} ${WHITE}\d \t ${BLUE}\u@\h: ${RED}\w${END}\n>>   "
unset RED BLUE YELLOW WHITE END
"""


# =============================================================================
# Define setup/general functions
# =============================================================================
def cprint(message, colour='g'):
    """
    print coloured message

    :param message: str, message to print
    :param colour: str, colour to print
    :return:
    """
    print(Colors.print(message, colour))


def ask(question, dtype=None, options=None, optiondesc=None, default=None,
        required=True):
    """
    Ask a question

    :param question: str, the question to ask
    :param dtype: str, the data type (int/float/bool/str/path/YN)
    :param options: list, list of valid options
    :param optiondesc: list, list of option descriptions
    :param default: object, if set the default value, if unset a value
                    if required
    :param required: bool, if False and dtype=path does not create a path
                     else does not change anything
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
    # deal with paths (expand)
    if isinstance(dtype, str) and dtype.upper() == 'PATH':
        default = os.path.expanduser(default)
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
        # record response
        if dtype == 'path':
            uinput = tab_input('')
            # strip spaces
            uinput = uinput.strip()
        else:
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
            elif not required:
                if uinput in ['None', '', None]:
                    check = False
                else:
                    cprint('Response must be a valid path or "None"', 'y')
                    check = True
                    continue
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
            if 'Y' in uinput.upper():
                return True
            elif 'N' in uinput.upper():
                return False
            else:
                cprint('Response must be [Y]es or [N]o', 'y')
                check = True
                continue
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
        else:
            check = False
    # deal with path
    if dtype == 'path':
        if '.' not in uinput:
            if not uinput.endswith(os.sep):
                uinput += os.sep

    # deal with returning default
    if uinput == '' and default is not None:
        return default
    else:
        # return uinput
        return uinput


def check_path_arg(name, value):
    promptuser = True
    # check if user config is None (i.e. set from cmd line)
    if value is not None:
        cprint('\t - {0} set from cmd ({1})'.format(name, value))
        if not os.path.exists(value):
            # check whether to create path
            pathquestion = 'Path "{0}" does not exist. Create?'
            promptuser = not ask(pathquestion.format(value), dtype='YN')
            # make the directory if we are not going to prompt the user
            if not promptuser:
                os.makedirs(value)
        # if path exists we do not need to prompt user
        else:
            promptuser = False
    # return prompt usr and value
    return promptuser, value


def user_interface(params, args):
    # set function name
    func_name = __NAME__ + '.user_interface()'
    # get default from params
    package = params['DRS_PACKAGE']
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()

    # deal with instrument from args
    if args.instrument is not None:
        drs_instruments = [args.instrument]
        one_instrument = True
    else:
        one_instrument = False

    # storage of answers
    all_params = dict()
    # title
    cprint(printheader(), 'm')
    cprint('Installation for {0}'.format(package), 'm')
    cprint(printheader(), 'm')
    print('\n')
    # ------------------------------------------------------------------
    # deal with having a profile name
    profilename = args.name
    # set default user path
    if profilename not in ['None', None, '']:
        profilename = profilename.strip().replace(' ', '_').lower()
        default_upath = DEFAULT_USER_PATH.replace('default', profilename)
        default_dpath = DEFAULT_DATA_PATH.replace('default', profilename)
    else:
        default_upath = DEFAULT_USER_PATH
        default_dpath = DEFAULT_DATA_PATH
    # ------------------------------------------------------------------
    # Step 1: Ask for user config path
    # ------------------------------------------------------------------
    promptuser, userconfig = check_path_arg('config', args.config)
    # if we still need to get user config ask user to get it
    if promptuser:
        userconfig = ask(message1, 'path', default=default_upath)
    # add user config to all_params
    all_params['USERCONFIG'] = userconfig
    # ------------------------------------------------------------------
    for instrument in drs_instruments:
        # ------------------------------------------------------------------
        cprint('\n' + printheader(), 'm')
        cprint('Settings for {0}'.format(instrument), 'm')
        cprint(printheader(), 'm')
        # ------------------------------------------------------------------
        # set up blank dictionary
        iparams = ParamDict()
        # ------------------------------------------------------------------
        # Step 2: Ask for instruments to install
        # ------------------------------------------------------------------
        # if one_instrument we know user already wants to install so dont' ask
        if not one_instrument:
            install = ask('Install {0}?'.format(instrument), dtype='YN')
            if not install:
                continue
            cprint(printheader(), 'g')
        # ------------------------------------------------------------------
        # set user config
        iparams['USERCONFIG'] = os.path.join(userconfig, instrument.lower())
        iparams.set_source('USERCONFIG', func_name)
        # make instrument user config directory
        if not os.path.exists(iparams['USERCONFIG']):
            os.mkdir(iparams['USERCONFIG'])
        # ------------------------------------------------------------------

        promptuser, datadir = check_path_arg('datadir', args.datadir)

        # check for data paths in args
        data_prompts, data_values = dict(), dict()
        data_promptuser = False
        for path in DATA_ARGS:
            if not promptuser:
                value = None
                promptuser1 = False
            else:
                value = getattr(args, DATA_ARGS[path])
                promptuser1, value = check_path_arg(path, value)
                data_prompts[path] = promptuser1
            data_values[path] = value
            data_promptuser |= promptuser1

        # ------------------------------------------------------------------
        # Step 3: Ask for data paths
        # ------------------------------------------------------------------

        if promptuser and data_promptuser:
            advanced = ask(message2, dtype='YN')
            cprint(printheader(), 'g')
        else:
            advanced = False
        # ------------------------------------------------------------------
        # if advanced then loop through all options
        if advanced:
            # loop around paths
            for path in DATA_PATHS:
                # get arg value
                promptuser = data_prompts[path]
                argvalue = data_values[path]
                if promptuser:
                    # get question and default
                    question, default = DATA_PATHS[path]
                    defaultpath = os.path.join(default_dpath, default)
                    # ask question and assign path
                    iparams[path] = ask(question, 'path', default=defaultpath)
                    iparams.set_source(path, __NAME__)
                    cprint(printheader(), 'g')
                else:
                    iparams[path] = argvalue
                    iparams.set_source(path, 'command line')
        # ------------------------------------------------------------------
        elif data_promptuser:
            create = False
            directory = default_dpath
            # loop until we have an answer
            while not create:
                directory = ask('Data directory', 'path',
                                default=default_dpath)
                # ask to create directory
                pathquestion = 'Path "{0}" does not exist. Create?'

                if not os.path.exists(directory):
                    create = ask(pathquestion.format(directory),
                                 dtype='YN')
                    if create:
                        os.makedirs(directory)
                        mkdir = '\n\t - Making directory "{0}"'
                        cprint(mkdir.format(directory), 'g')
                else:
                    create = True
            # loop around paths and create them
            for path in DATA_PATHS:
                # get questions and default
                question, default = DATA_PATHS[path]
                # assign path
                iparams[path] = os.path.join(directory, default)
                iparams.set_source(path, __NAME__)
                # check whether path exists
                if not os.path.exists(iparams[path]):
                    os.makedirs(iparams[path])
                    mkdir = '\n\t - Making directory "{0}"'
                    cprint(mkdir.format(iparams[path]), 'g')
            cprint(printheader(), 'g')

        else:
            for path in DATA_PATHS:
                # get questions and default
                question, default = DATA_PATHS[path]
                value = data_values[path]
                if value is None and datadir is not None:
                    iparams[path] = os.path.join(datadir, default)
                    iparams.set_source(path, 'command line + default')
                    pargs = [path, iparams[path]]
                    cprint('\t - {0} set from datadir ({1})'.format(*pargs))
                else:
                    # assign path
                    iparams[path] = value
                    iparams.set_source(path, 'command line')

        # ------------------------------------------------------------------
        # Step 4: Ask for plot mode
        # ------------------------------------------------------------------
        # find value in args
        if args.plotmode is None:

            plot = ask('Plot mode required', dtype='int', options=[0, 1, 2],
                       optiondesc=['0: No plotting',
                                   '1: Plots display at end of code',
                                   '2: Plots display immediately and '
                                   'pause code'],
                       default=0)
            iparams['DRS_PLOT'] = plot
            iparams.set_source('DRS_PLOT', __NAME__)
            # add header line
            cprint(printheader(), 'g')
        else:
            cprint('\t - DRS_PLOT set from cmd ({0})'.format(args.plotmode))
            iparams['DRS_PLOT'] = args.plotmode
            iparams.set_source('DRS_PLOT', 'command line')

        # ------------------------------------------------------------------
        # Step 5: Ask whether we want a clean install
        # ------------------------------------------------------------------
        if args.clean is None:
            iparams['CLEAN_INSTALL'] = ask(message3, dtype='YN')
            iparams.set_source('CLEAN_INSTALL', func_name)
        else:
            cprint('\t - CLEAN set from cmd ({0})'.format(args.clean))
            iparams['CLEAN_INSTALL'] = eval(args.clean)
            iparams.set_source('CLEAN_INSTALL', 'command line')

        # ------------------------------------------------------------------
        # Step 6: Check for programs
        # ------------------------------------------------------------------
        if args.ds9path is None or args.pdfpath is None:
            # set the values of ds9path and pdfpath initial to None
            ds9path, pdfpath = None, None
            # ------------------------------------------------------------------
            # ds9 path
            # ------------------------------------------------------------------
            # add header line
            cprint(printheader(), 'g')
            cprint('Recommended external programs (optional)')
            # check command line args
            if args.ds9path is not None:
                if args.ds9path == 'None':
                    promptuser, ds9path = False, None

                else:
                    promptuser, ds9path = check_path_arg('ds9dir', args.datadir)
            # get ds9
            if 'DRS_DS9_PATH' in all_params:
                ds9path = all_params['DRS_DS9_PATH']
            elif ds9path is None:
                ds9path = shutil.which('ds9')
            # deal with no ds9 path found
            if ds9path is None and promptuser:
                iparams['DRS_DS9_PATH'] = ask(message5, dtype='path',
                                              default='None', required=False)
                iparams.set_source('DRS_DS9_PATH', 'user')
            else:
                iparams['DRS_DS9_PATH'] = ds9path
                iparams.set_source('DRS_DS9_PATH', func_name)
                cprint('\n\t - Found ds9', 'g')
            # add it/update all_params
            all_params['DRS_DS9_PATH'] = ds9path
            # ------------------------------------------------------------------
            # pdf latex path
            # ------------------------------------------------------------------
            # check command line args
            if args.pdfpath is not None:
                if args.pdfpath == 'None':
                    promptuser, pdfpath = False, args.pdfpath

                else:
                    promptuser, pdfpath = check_path_arg('pdfdir', args.pdfpath)
            # get pdflatex
            if 'DRS_PDFLATEX_PATH' in all_params:
                pdfpath = all_params['DRS_PDFLATEX_PATH']
            elif pdfpath is None:
                pdfpath = shutil.which('pdflatex')
            # deal with no ds9 path found
            if pdfpath is None and promptuser:
                iparams['DRS_PDFLATEX_PATH'] = ask(message6, dtype='path',
                                                   default='None',
                                                   required=False)
                iparams.set_source('DRS_PDFLATEX_PATH', 'user')
            else:
                iparams['DRS_PDFLATEX_PATH'] = pdfpath
                iparams.set_source('DRS_PDFLATEX_PATH', func_name)
                cprint('\n\t - Found pdflatex', 'g')
            # add it/update all_params
            all_params['DRS_PDFLATEX_PATH'] = pdfpath
        else:
            cprint('\t - DS9PATH set from cmd ({0})'.format(args.ds9path))
            cprint('\t - PDFPATH set from cmd ({0})'.format(args.pdfpath))
        # ------------------------------------------------------------------
        # add iparams to all params
        all_params[instrument] = iparams
        # ------------------------------------------------------------------
    cprint(printheader(), 'm')
    # ----------------------------------------------------------------------
    # return all parameters
    return all_params


# =============================================================================
# Define installation functions
# =============================================================================
def bin_paths(params, all_params):
    # get package
    package = params['DRS_PACKAGE']
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()
    # get root path
    root = constants.get_relative_folder(package, '')
    # get out bin path
    out_bin_path = constants.get_relative_folder(package, OUT_BINPATH)
    # get out tools bin path
    out_tool_path = constants.get_relative_folder(package, OUT_TOOLPATH)
    # get tools save location
    in_tool_path = constants.get_relative_folder(package, IN_TOOLPATH)
    # add recipe bin directory to all params
    all_params['DRS_OUT_BIN_PATH'] = out_bin_path
    # add toool directory to all params
    all_params['DRS_OUT_TOOL_PATH'] = out_tool_path
    # add the drs root directory to all params
    all_params['DRS_ROOT'] = root
    # add the individual tool directories to all params
    all_params['DRS_OUT_TOOLS'] = []
    for directory in os.listdir(in_tool_path):
        # make out tool paths
        out_tools = os.path.join(out_tool_path, directory)
        # append out tool paths to drs out tools
        all_params['DRS_OUT_TOOLS'].append(out_tools)
    # loop through instruments
    for instrument in drs_instruments:
        # only deal with instrument user wants to set up
        if instrument not in list(all_params.keys()):
            continue
        # add drs root to all_params
        all_params[instrument]['DRS_ROOT'] = root
    # return the updated all params
    return all_params


def create_configs(params, all_params):
    # set function name
    func_name = __NAME__ + '.create_configs()'
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()
    # get config directory
    userconfig = all_params['USERCONFIG']
    # get dev mode
    devmode = all_params['DEVMODE']
    # loop around instruments
    for instrument in drs_instruments:
        if instrument in all_params:
            # load params for instrument
            iparams = constants.load(instrument.upper(), from_file=False,
                                     cache=False)
            # load params for all_params
            aparams = all_params[instrument]
            uargs = [iparams, instrument, devmode]
            config_lines, const_lines = create_ufiles(*uargs)
            # get user path
            upath = os.path.join(userconfig, instrument.lower())
            # write / update config and const
            uconfig = ufile_write(aparams, config_lines, upath, UCONFIG,
                                  'config')
            uconst = ufile_write(aparams, const_lines, upath, UCONST,
                                 'constant')
            # store filenames in iparams
            all_params[instrument]['CONFIGFILES'] = [uconfig, uconst]
            all_params[instrument].set_source('CONFIGFILES', func_name)
    # return all_params
    return all_params


def update_configs(params, all_params):
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()
    # loop around instruments
    for instrument in drs_instruments:
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


def create_shell_scripts(params, all_params):
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()
    # ----------------------------------------------------------------------
    # get package
    package = params['DRS_PACKAGE']
    if all_params['PROFILENAME'] not in [None, 'None', '']:
        pname = all_params['PROFILENAME'].replace(' ', '_')
    else:
        pname = package
    # get tools save location
    in_tool_path = constants.get_relative_folder(package, IN_TOOLPATH)
    # ----------------------------------------------------------------------
    # get paths and add in correct order
    paths = [os.path.dirname(all_params['DRS_ROOT'])]
    # add bin directory
    paths.append(all_params['DRS_OUT_BIN_PATH'])
    # add all the tool directories
    for directory in all_params['DRS_OUT_TOOLS']:
        paths.append(directory)
    # ----------------------------------------------------------------------
    # find setup files
    setup_path = constants.get_relative_folder(package, SETUP_PATH)
    # deal with windows
    if os.name == 'nt':
        sep = '";"'
        setup_infiles = ['{0}.win.setup'.format(package.lower())]
        setup_outfiles = ['{0}.win.setup'.format(pname.lower())]
    # deal with unix
    elif os.name == 'posix':
        sep = '":"'
        setup_infiles = ['{0}.bash.setup'.format(package.lower())]
        setup_infiles += ['{0}.sh.setup'.format(package.lower())]
        setup_outfiles = ['{0}.bash.setup'.format(pname.lower())]
        setup_outfiles += ['{0}.sh.setup'.format(pname.lower())]
    # else generate error message
    else:
        # print error message
        emsg = 'Error {0} does not support OS (OS = {0})'
        cprint(emsg.format(os.name), 'red')
        sys.exit()
    # ----------------------------------------------------------------------
    # construct validation code absolute path
    valid_path = os.path.join(in_tool_path, VALIDATE_CODE)
    # ----------------------------------------------------------------------
    # setup text dictionary
    text = dict()
    text['ROOT_PATH'] = os.path.dirname(all_params['DRS_ROOT'])
    text['USER_CONFIG'] = all_params['USERCONFIG']
    text['NAME'] = all_params['PROFILENAME']
    text['PATH'] = '"' + sep.join(paths) + '"'
    text['PYTHONPATH'] = '"' + sep.join(paths) + '"'
    # ----------------------------------------------------------------------
    # loop around setup files
    for it, setup_file in enumerate(setup_infiles):
        # deal with having profile name
        if all_params['PROFILENAME'] not in [None, 'None', '']:
            # get absolute path
            inpath = os.path.join(setup_path, setup_file + '.profile')
        else:
            # get absolute path
            inpath = os.path.join(setup_path, setup_file)
        # get output path
        outpath = os.path.join(all_params['USERCONFIG'], setup_outfiles[it])
        # ------------------------------------------------------------------
        # make sure in path exists
        if not os.path.exists(inpath):
            emsg = 'Error setup file "{0}" does not exist'
            cprint(emsg.format(inpath), 'red')
            sys.exit()
        # ------------------------------------------------------------------
        # make sure out path does not exist
        if os.path.exists(outpath):
            os.remove(outpath)
        # ------------------------------------------------------------------
        # read setup file
        in_setup = open(inpath, 'r')
        # read setup lines
        in_lines = in_setup.readlines()
        # close setup file
        in_setup.close()
        # ------------------------------------------------------------------
        # loop around lines and update parameters
        out_lines = []
        for in_line in in_lines:
            # construct new line
            out_line = in_line.format(**text)
            # add to new lines
            out_lines.append(out_line)
        # ------------------------------------------------------------------
        # add instrument tests
        for instrument in drs_instruments:
            out_lines.append('\n')
            if instrument in all_params:
                # run the validation script (just to print splash)
                comment = ('# run the validation script for {0}'
                           ''.format(instrument))
                command = 'python {0} {1}'.format(valid_path, instrument)
                # add to out lines
                out_lines.append(comment + '\n')
                out_lines.append(command + '\n')
        # ------------------------------------------------------------------
        # open output setup file
        out_setup = open(outpath, 'w')
        # write lines to out setup file
        out_setup.writelines(out_lines)
        # close out setup file
        out_setup.close()
    # return all params
    return all_params


def clean_install(params, all_params):
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()
    # get package
    package = params['DRS_PACKAGE']
    # get tools save location
    in_tool_path = constants.get_relative_folder(package, IN_TOOLPATH)
    # append tool path
    sys.path.append(os.path.join(in_tool_path, 'bin'))
    toolmod = importlib.import_module(RESET_CODE)
    # loop around instruments
    for instrument in drs_instruments:
        # skip is we are not installing instrument
        if instrument not in all_params:
            continue
        # check if all directories are empty
        cond1 = not reset_paths_empty(params, all_params, instrument)
        cond2 = not all_params[instrument]['CLEAN_INSTALL']
        # check if user wants a clean install
        if cond1 and cond2:
            continue
        # if we are forcing clean install let the user know
        if not cond1:
            cprint('\t - Empty directory found -- forcing clean install.', 'y')
        # log that we are performing clean install
        cprint('\t - Performing clean installation', 'm')
        # add to environment
        add_paths(all_params)
        # construct reset command
        toolmod.main(instrument=instrument, quiet=True, warn=True)
    # return all params
    return all_params


def create_symlinks(params, all_params):
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()
    # get package
    package = params['DRS_PACKAGE']
    # get out paths
    out_bin_path = all_params['DRS_OUT_BIN_PATH']
    out_tool_path = all_params['DRS_OUT_TOOL_PATH']
    # get tools save location
    in_tool_path = constants.get_relative_folder(package, IN_TOOLPATH)

    # ------------------------------------------------------------------
    # Copy bin files (for each instrument)
    # ------------------------------------------------------------------
    # log which directory we are populating
    cprint('\n\t Populating {0} directory\n'.format(out_bin_path), 'm')

    # loop around instruments
    for instrument in drs_instruments:
        # skip is we are not installing instrument
        if instrument not in all_params:
            continue

        # find recipe folder for this instrument
        recipe_raw = IN_BINPATH.format(instrument.lower())
        recipe_dir = constants.get_relative_folder(package, recipe_raw)
        # define suffix
        suffix = '*_{0}.py'.format(instrument.lower())
        # create sym links
        _create_link(recipe_dir, suffix, out_bin_path)

    # ------------------------------------------------------------------
    # Copy tools (do not copy tools directories for instruments not being
    #    installed)
    # ------------------------------------------------------------------
    # get list of tool directories
    dirs = os.listdir(in_tool_path)

    for directory in dirs:
        # do not copy tools for instruments we are not installing
        if directory.upper() in drs_instruments:
            if directory .upper() not in all_params:
                continue

        # construct this directories absolute path
        in_tools = os.path.join(in_tool_path, directory)
        out_tools = os.path.join(out_tool_path, directory)

        # log which directory we are populating
        cprint('\n\t Populating {0} directory\n'.format(out_tools), 'm')
        # define suffix
        suffix = '*.py'
        # create sym links
        _create_link(in_tools, suffix, out_tools)

    # ------------------------------------------------------------------
    # return all_params
    return all_params


def _create_link(recipe_dir, suffix, new_path, log=True):
    # get all python files in recipe folder
    files = glob.glob(os.path.join(recipe_dir, suffix))
    # loop around files and create symbolic links in bin path
    for filename in files:
        # get file base name
        basename = os.path.basename(filename)
        # construct new path
        newpath = os.path.join(new_path, basename)
        if log:
            cprint('\t\tMoving {0}'.format(basename))
        # remove link already present
        if os.path.exists(newpath) or os.path.islink(newpath):
            os.remove(newpath)
        # deal with directories not exists
        if not os.path.exists(os.path.dirname(newpath)):
            os.makedirs(os.path.dirname(newpath))
        # make symlink
        os.symlink(filename, newpath)
        # make executable
        try:
            os.chmod(newpath, 0o777)
        except:
            cprint('Error: Cannot chmod 777', 'r')


def add_paths(all_params):
    # get paths and add in correct order
    paths = [os.path.dirname(all_params['DRS_ROOT'])]
    # add bin directory
    paths.append(all_params['DRS_OUT_BIN_PATH'])
    # add all the tool directories
    for directory in all_params['DRS_OUT_TOOLS']:
        paths.append(directory)
    # ----------------------------------------------------------------------
    # set USERCONFIG
    os.environ[ENV_CONFIG] = all_params['USERCONFIG']
    # ----------------------------------------------------------------------
    if os.name == 'posix':
        sep = ':'
    else:
        sep = ';'
    # ----------------------------------------------------------------------
    # add to PATH
    if 'PATH' in os.environ:
        # get old path
        oldpath = os.environ['PATH']
        # add to paths
        paths += oldpath
        # add to environment
        os.environ['PATH'] = sep.join(paths)
    else:
        # add to environment
        os.environ['PATH'] = sep.join(paths)
    # add to PYTHON PATH
    if 'PYTHONPATH' in os.environ:
        oldpath = os.environ['PYTHONPATH']
        # add to paths
        paths += oldpath
        # add to environment
        os.environ['PYTHONPATH'] = sep.join(paths)
    else:
        # add to environment
        os.environ['PYTHONPATH'] = sep.join(paths)


def printheader():
    rows, columns = constants.param_functions.window_size()
    return '=' * (columns - 1)


def print_options(params, all_params):
    # set up the text dictionary
    text = dict()

    # deal with user config (should end with os.sep)
    userconfig = all_params['USERCONFIG']
    if not userconfig.endswith(os.sep):
        userconfig += os.sep
    # add to text dictionary
    text['DRS_UCONFIG'] = userconfig
    # add system to text dictionary
    text['SYSTEM'] = '{SYSTEM}'
    # add profile name (package name)
    if all_params['PROFILENAME'] not in ['None', None, '']:
        text['NAME'] = all_params['PROFILENAME']
    else:
        text['NAME'] = params['DRS_PACKAGE']
    # print the messages
    print('\n\n')
    cprint(printheader(), 'm')
    cprint(' To run apero do one of the following:', 'm')
    cprint(printheader(), 'm')
    cprint(message4.format(**text), 'g')


def reset_paths_empty(params, all_params, instrument=None):

    if instrument is None:
        instruments = params['DRS_INSTRUMENTS']
    else:
        instruments = [instrument]
    # loop around instruments
    for instrument in instruments:
        # skip if we are not installing instrument
        if instrument not in all_params:
            continue
        # get instrument params
        iparams = all_params[instrument]
        # look for paths
        for path in RESET_PATHS:
            # get instrument path
            ipath = iparams[path]
            # check for empty
            if len(os.listdir(ipath)) == 0:
                return True
    # if we have got here return False --> none are empty
    return False


# =============================================================================
# create user files functions
# =============================================================================
def create_ufiles(params, instrument, devmode):
    # storage of parameters of different types
    config = OrderedDict()
    const = OrderedDict()
    # ------------------------------------------------------------------
    config_groups = []
    const_groups = []
    # ------------------------------------------------------------------
    # dev groups
    dev_groups = dict()

    # ------------------------------------------------------------------
    # loop around all parameters and find which need to be added
    #  to config file and const file
    for param in params:
        # ------------------------------------------------------------------
        # get instance
        instance = params.instances[param]
        # if we don't have instance we continue
        if instance is None:
            continue
        # get group name
        group = instance.group
        # get user variable
        user = instance.user
        # ------------------------------------------------------------------
        # if we have no group we don't want this in config files
        if group is None:
            continue
        # if user if False we don't want this in config files
        if user is False and not devmode:
            continue
        # ------------------------------------------------------------------
        # get source of data
        source = params.sources[param]
        # get config/const
        if 'user_config' in source:
            kind = 'config'
        elif 'default_config' in source:
            kind = 'config'
        elif 'default_constants' in source:
            kind = 'const'
        elif 'user_constants' in source:
            kind = 'const'
        else:
            continue
        # ------------------------------------------------------------------
        # deal with asking the user for groups in devmode
        if devmode and user is False:
            # deal with first time seeing this group
            if group not in dev_groups:
                cprint(printheader(), 'g')
                umessage = ('DEV MODE: Add all constants in group "{0}" '
                            'to {1} file?')
                output = ask(umessage.format(group, kind), dtype='YN')
                dev_groups[group] = output
            # else skip if user has choosen that they don't want this group
            if not dev_groups[group]:
                continue
        # ------------------------------------------------------------------
        # add group to group storage (in correct order)
        if kind == 'config' and group not in config_groups:
            config_groups.append(group)
        elif group not in const_groups:
            const_groups.append(group)
        # ------------------------------------------------------------------
        # decide on group
        if kind == 'config':
            if group in config:
                config[group].append([instance, params[param]])
            else:
                config[group] = [[instance, params[param]]]
        elif kind == 'const':
            if group in const:
                const[group].append([instance, params[param]])
            else:
                const[group] = [[instance, params[param]]]
    # ------------------------------------------------------------------
    # create config file
    config_lines = create_ufile(instrument, 'config', config, config_groups,
                                devmode)
    # create const file
    const_lines = create_ufile(instrument, 'constant', const, const_groups,
                               devmode)
    # ------------------------------------------------------------------
    return config_lines, const_lines


def create_ufile(instrument, kind, dictionary, grouplist, devmode):
    lines = []
    lines += user_header('{0} {1} file'.format(instrument, kind))
    # loop around groups
    for group in grouplist:
        # only add if we have parameters that are needed in that group
        if group in dictionary:
            # add a header if this is a new group
            lines += ['']
            lines += user_header(group)
            # loop around group parameters
            for item in range(len(dictionary[group])):
                # get instance of this parameter
                instance = dictionary[group][item][0]
                # get value of this parameter
                value = dictionary[group][item][1]
                # create line
                lines += instance.write_line(value=value)
    # return lines
    return lines


def user_header(title):
    lines = []
    lines.append('# {0}'.format('-' * 77))
    lines.append('# ')
    lines.append('#  {0}'.format(title))
    lines.append('# ')
    lines.append('# {0}'.format('-' * 77))
    return lines


def ufile_write(aparams, lines, upath, ufile, kind):
    # make directory if it doesn't exist
    if not os.path.exists(upath):
        os.makedirs(upath)
    # ----------------------------------------------------------------------
    # define config file path
    ufilepath = os.path.join(upath, ufile)
    # ----------------------------------------------------------------------
    # deal with config file existing
    if os.path.exists(ufilepath):
        # need to open current
        u_file = open(ufilepath, 'r')
        current_lines = u_file.readlines()
        u_file.close()
        # now need to check these lines against lines
        for l_it, line in enumerate(lines):
            # we shouldn't worry about old comment lines
            if line.strip().startswith('#'):
                continue
            if len(line) == 0:
                continue
            # get variable name
            variable, value = line.split('=')
            variable = variable.strip()
            value = value.strip()
            cvalue, cline = None, ''
            # do not correct variables that we will automatically set later
            #   ( set by user)
            if variable in aparams:
                continue
            # loop around current lines
            for c_it, cline in enumerate(current_lines):
                if cline.strip().startswith('#'):
                    continue
                if len(cline) == 0:
                    continue
                if variable in cline:
                    cvariable, cvalue = cline.split('=')
                    cvariable = cvariable.strip()
                    cvalue = cvalue.strip().strip('\n')
                    # only if we have a matching variable
                    if cvariable == variable:
                        break
            # if line is the same we continue
            if value == cvalue:
                continue
            # deal with line found
            elif cvalue is not None:
                # display a warning
                umessage1 = ('\nConflicting line found in current {0} file for'
                             'constant "{1}"')
                cprint(umessage1.format(kind, variable), 'y')
                umessage2 = 'Replace default:\n\t{0} \n with current:\n\t{1}'
                output = ask(umessage2.format(value, cvalue), dtype='YN')
                if output:
                    lines[l_it] = cline
    # ----------------------------------------------------------------------
    # write files
    u_file = open(ufilepath, 'w')
    for line in lines:
        if not line.endswith('\n'):
            u_file.write(line + '\n')
        else:
            u_file.write(line)
    u_file.close()
    # return user file path
    return ufilepath


# =============================================================================
# update functions
# =============================================================================
def update(params, args):
    # set function name
    func_name = __NAME__ + '.update()'
    # get available instruments
    drs_instruments = np.char.array(params['DRS_INSTRUMENTS']).upper()
    # get config path
    config_env = params['DRS_USERENV']
    # check for config environment set
    config_path = os.getenv(config_env)
    # deal with no config path set
    if config_path is None:
        cprint('Error: Cannot run update. Must be in apero environment '
               '(i.e. source apero.{SYSTEM}.setup).', 'r')
        sys.exit()
    # ----------------------------------------------------------------------
    # find all installed instruments
    instruments = []
    files = os.listdir(config_path)
    # loop through filenames
    for filename in files:
        # get abspath
        abspath = os.path.join(config_path, filename)
        # check if valid instrument
        if os.path.isdir(abspath) and filename.upper() in drs_instruments:
            instruments.append(filename.upper())
    # ----------------------------------------------------------------------
    # set up dictionary
    all_params = dict()
     # loop around instruments
    for instrument in instruments:
        # ------------------------------------------------------------------
        # set up instrument storage
        istorage = ParamDict()
        # add user config
        all_params['USERCONFIG'] = config_path
        istorage['USERCONFIG'] = config_path
        istorage.set_source('USERCONFIG', func_name)
        # load params for instrument
        iparams = constants.load(instrument.upper(), cache=False)
        # ------------------------------------------------------------------
        # loop around data paths
        for datapath in DATA_PATHS.keys():
            # get data paths
            istorage[datapath] = str(iparams[datapath])
            istorage.set_source(datapath, iparams.sources[datapath])
        # ------------------------------------------------------------------
        # add clean install
        if args.clean in ['True', True, '1', 1]:
            istorage['CLEAN_INSTALL'] = True
            istorage.set_source('CLEAN_INSTALL', 'sys.argv')
        else:
            istorage['CLEAN_INSTALL'] = False
            istorage.set_source('CLEAN_INSTALL', func_name)
        # add ds9
        istorage['DRS_DS9_PATH'] = iparams['DRS_DS9_PATH']
        istorage.set_source('DRS_DS9_PATH', iparams.sources['DRS_DS9_PATH'])
        # add pdflatex
        istorage['DRS_PDFLATEX_PATH'] = iparams['DRS_PDFLATEX_PATH']
        istorage.set_source('DRS_PDFLATEX_PATH',
                            iparams.sources['DRS_PDFLATEX_PATH'])
        # ------------------------------------------------------------------
        # add to all_params
        all_params[instrument] = istorage
    # return all params
    return all_params


# =============================================================================
# Define functions
# =============================================================================
class PathCompleter(object):
    """
    Copy of
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
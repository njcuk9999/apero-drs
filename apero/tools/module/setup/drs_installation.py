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
import readline
import glob

from apero.core import constants
from apero.core.instruments.default import pseudo_const
from apero.locale import drs_exceptions

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
DEFAULT_USER_PATH = '~/apero/config/'
DEFAULT_DATA_PATH = '~/apero/data/'

BINPATH = '../bin/'
TOOLPATH = '../apero/tools/bin/'
RECIPEPATH = './recipes/{0}/'
ENV_CONFIG = 'DRS_UCONFIG'
SETUP_PATH = './tools/resources/setup/'


DATA_PATHS = dict()
DATA_PATHS['DRS_DATA_RAW'] = ['Raw data directory', 'raw']
DATA_PATHS['DRS_DATA_WORKING'] = ['Temporary data directory', 'tmp']
DATA_PATHS['DRS_DATA_REDUC'] = ['Reduced data directory', 'reduced']
DATA_PATHS['DRS_CALIB_DB'] = ['Calibration DB data directory', 'calibDB']
DATA_PATHS['DRS_TELLU_DB'] = ['Telluric DB data directory', 'telluDB']
DATA_PATHS['DRS_DATA_PLOT'] = ['Plotting directory', 'plot']
DATA_PATHS['DRS_DATA_RUN'] = ['Run directory', 'runs']
DATA_PATHS['DRS_DATA_MSG'] = ['Log directory', 'msg']

# Messages for user interface
message1 = """
User config path: 

    This is the path where your user configuration will be saved.
    If it doesn't exist you will be prompted to create it. 
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
"""

message4 = """

    i) Add an alias in your ~/.bashrc or ~/.bash_profile or 
       ~/.tcshrc or ~/.profile 
       and then type "apero" every time you wish to run apero.
       i.e. for bash
            alias apero="source {DRS_UCONFIG}apero.bash.setup"
       i.e. for sh
            alias apero "source {DRS_UCONFIG}apero.sh.setup"
    
    
    ii) Add the contents of {DRS_UCONFIG}apero.{SYSTEM}.setup 
        to your ~/.bashrc or ~/.bash_profile or ~/.tcshrc or ~/.profile
    

    iii) type "source {DRS_UCONFIG}apero.{SYSTEM}.setup" every 
         time you wish to run apero.
           i.e. for bash
                source {DRS_UCONFIG}apero.bash.setup
           i.e. for sh
                source {DRS_UCONFIG}apero.sh.setup


Note: here {SYSTEM} is "bash" or "sh" or "win" depending on your system.


"""


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
    # set function name
    func_name = __NAME__ + '.user_interface()'
    # get default from params
    package = params['DRS_PACKAGE']
    # storage of answers
    all_params = dict()
    # title
    cprint(printheader(), 'm')
    cprint('Installation for {0}'.format(package), 'm')
    cprint(printheader(), 'm')
    print('\n')
    # ------------------------------------------------------------------
    # Step 1: Ask for user config path
    userconfig = ask(message1, 'path', default=DEFAULT_USER_PATH)
    all_params['USERCONFIG'] = userconfig
    # ------------------------------------------------------------------
    for instrument in INSTRUMENTS:
        # ------------------------------------------------------------------
        cprint('\n' + printheader(), 'm')
        cprint('Settings for {0}'.format(instrument), 'm')
        cprint(printheader(), 'm')
        # ------------------------------------------------------------------
        # set up blank dictionary
        iparams = ParamDict()
        # ------------------------------------------------------------------
        # Step 2: Ask for instruments to install
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
        # Step 3: Ask for data paths
        advanced = ask(message2, dtype='YN')
        cprint(printheader(), 'g')
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
                cprint(printheader(), 'g')
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
                        cprint(printheader(), 'g')
                        created = True
            if not created:
                cprint(printheader(), 'g')
        # ------------------------------------------------------------------
        # Step 4: Ask for plot mode
        plot = ask('Plot mode required', dtype='int', options=[0, 1, 2],
                   optiondesc=['0: No plotting',
                               '1: Plots display at end of code',
                               '2: Plots display immediately and pause code'],
                   default=0)
        iparams['DRS_PLOT'] = plot
        iparams.set_source('DRS_PLOT', __NAME__)
        # add header line
        cprint(printheader(), 'g')
        # ------------------------------------------------------------------
        # Step 5: Ask whether we want a clean install
        iparams['CLEAN_INSTALL'] = ask(message3, dtype='YN')
        iparams.set_source('CLEAN_INSTALL', func_name)
        # ------------------------------------------------------------------
        # add iparams to all params
        all_params[instrument] = iparams

    cprint(printheader(), 'm')
    # ----------------------------------------------------------------------
    # return all parameters
    return all_params


def copy_configs(params, all_params):
    # set function name
    func_name = __NAME__ + '.copy_configs()'

    # get properties from iparams
    duser_config = params['DRS_USER_DEFAULT']
    package = params['DRS_PACKAGE']
    # get installation root
    all_params['DRS_ROOT'] = constants.get_relative_folder(package, '')
    # loop around instruments
    for instrument in INSTRUMENTS:
        # only deal with instrument user wants to set up
        if instrument not in list(all_params.keys()):
            continue
        # get iparams
        iparams = all_params[instrument]
        iparams['DRS_ROOT'] = all_params['DRS_ROOT']
        iparams.set_source('DRS_ROOT', func_name)
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
        iparams.set_source('CONFIGFILES', func_name)
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


def bin_paths(params, all_params):
    # get package
    package = params['DRS_PACKAGE']
    # add bin path
    bin_path = constants.get_relative_folder(package, BINPATH)
    # add tools bin path
    tool_path = constants.get_relative_folder(package, TOOLPATH)
    # add to all_params
    all_params['DRS_BIN_PATH'] = bin_path
    all_params['DRS_TOOL_PATH'] = tool_path
    # return the updated all params
    return all_params


def create_shell_scripts(params, all_params):
    # get package
    package = params['DRS_PACKAGE']
    # find setup files
    setup_path = constants.get_relative_folder(package, SETUP_PATH)

    # deal with windows
    if os.name == 'nt':
        setup_files = ['{0}.win.setup'.format(package.lower())]
    # deal with unix
    elif os.name == 'posix':
        setup_files = ['{0}.bash.setup'.format(package.lower())]
        setup_files += ['{0}.sh.setup'.format(package.lower())]
    # else generate error message
    else:
        # print error message
        emsg = 'Error {0} does not support OS (OS = {0})'
        cprint(emsg.format(os.name), 'red')
        sys.exit()

    # construct validation code absolute path
    valid_path = os.path.join(all_params['DRS_TOOL_PATH'], 'validate.py')
    # ----------------------------------------------------------------------
    # setup text dictionary
    text = dict()
    text['BIN_PATH'] = all_params['DRS_BIN_PATH']
    text['TOOL_PATH'] = all_params['DRS_TOOL_PATH']
    text['USER_CONFIG'] = all_params['USERCONFIG']
    text['ROOT_PATH'] = os.path.dirname(all_params['DRS_ROOT'])
    # ----------------------------------------------------------------------
    # loop around setup files
    for setup_file in setup_files:
        # get absolute path
        inpath = os.path.join(setup_path, setup_file)
        # get output path
        outpath = os.path.join(all_params['USERCONFIG'], setup_file)
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
        for instrument in INSTRUMENTS:
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


def clean_install(all_params):
    # get root directory
    binpath = all_params['DRS_TOOL_PATH']
    # loop around instruments
    for instrument in INSTRUMENTS:
        # skip is we are not installing instrument
        if instrument not in all_params:
            continue
        # check if user wants a clean install
        if not all_params[instrument]['CLEAN_INSTALL']:
            continue
        # log that we are performing clean install
        cprint('\t - Performing clean installation', 'm')
        # add to environment
        add_paths(all_params)
        # construct reset command
        cmd = 'python {0}/reset.py {1} --quiet'.format(binpath, instrument)
        # run command
        os.system(cmd)
    # return all params
    return all_params


def create_symlinks(params, all_params):
    # get root directory
    binpath = all_params['DRS_BIN_PATH']
    # get package
    package = params['DRS_PACKAGE']
    # loop around instruments
    for instrument in INSTRUMENTS:
        # skip is we are not installing instrument
        if instrument not in all_params:
            continue
        # find recipe folder for this instrument
        recipe_raw = RECIPEPATH.format(instrument.lower())
        recipe_dir = constants.get_relative_folder(package, recipe_raw)
        # define suffix
        suffix = '*_{0}.py'.format(instrument.lower())
        # get all python files in recipe folder
        files = glob.glob(os.path.join(recipe_dir, suffix))
        # loop around files and create symbolic links in bin path
        for filename in files:
            # get file base name
            basename = os.path.basename(filename)
            # construct new path
            newpath = os.path.join(binpath, basename)
            cprint('\tMoving {0}'.format(basename))
            # remove link already present
            if os.path.exists(newpath):
                os.remove(newpath)
            # make symlink
            os.symlink(filename, newpath)
            # make executable
            try:
                os.chmod(newpath, 0o777)
            except:
                cprint('Error: Cannot chmod 777', 'r')
    # return all_params
    return all_params


def add_paths(all_params):
    # get paths
    bin_path = all_params['DRS_BIN_PATH']
    tool_path = all_params['DRS_TOOL_PATH']
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
        oldpath = os.environ['PATH']
        args = [sep, bin_path, tool_path, oldpath]
        os.environ['PATH'] = '{1}{0}{2}{0}{3}'.format(*args)
    else:
        args = [sep, bin_path, tool_path]
        os.environ['PATH'] = '{1}{0}{2}'.format(*args)
    # add to PYTHON PATH
    if 'PYTHONPATH' in os.environ:
        oldpath = os.environ['PYTHONPATH']
        args = [sep, bin_path, tool_path, oldpath]
        os.environ['PYTHONPATH'] = '{1}{0}{2}{0}{3}'.format(*args)
    else:
        args = [sep, bin_path, tool_path]
        os.environ['PYTHONPATH'] = '{1}{0}{2}'.format(*args)


def printheader():
    rows, columns = constants.param_functions.window_size()
    return '=' * (columns - 1)


def print_options(params, all_params):
    # set up the text dictionary
    text = dict()
    text['DRS_UCONFIG'] = all_params['USERCONFIG']
    text['SYSTEM'] = '{SYSTEM}'
    # print the messages
    print('\n\n')
    cprint(printheader(), 'm')
    cprint(' To run apero do one of the following:', 'm')
    cprint(printheader(), 'm')
    cprint(message4.format(**text), 'g')


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
    # print 'Hello World!'
    print("Hello World!")


# =============================================================================
# End of code
# =============================================================================
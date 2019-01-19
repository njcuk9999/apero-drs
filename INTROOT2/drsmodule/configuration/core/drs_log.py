#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
spirouCore.py

Logging related functions

Created on 2017-10-11 at 10:59

@author: cook

Import rules: Only from spirouConfig and spirouCore

Version 0.0.1
"""
from __future__ import division
import os
import sys
import warnings

from drsmodule import constants
from drsmodule.configuration.math import time

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'log.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(None)
# Get version and author
__version__ = Constants['VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DATE']
__release__ = Constants['RELEASE']
# Get the parameter dictionary
ParamDict = constants.ParamDict
# Get the Config error
ConfigError = constants.ConfigError
# Get the Color dict
Color = constants.Colors


# =============================================================================
# Define classes
# =============================================================================
class Logger:
    def __init__(self, paramdict=None, instrument=None):
        """
        Construct logger (storage param dict here)
        :param paramdict:
        """
        # ---------------------------------------------------------------------
        # save the parameter dictionary for access to constants
        if paramdict is not None:
            self.pin = paramdict
            self.instrument = paramdict['INSTRUMENT']
            self.pconstant = constants.pload(self.instrument)
        elif instrument is not None:
            self.pin = constants.load(instrument)
            self.instrument = instrument
            self.pconstant = constants.pload(instrument)
        else:
            self.pin = constants.load()
            self.instrument = None
            self.pconstant = constants.pload()
        # ---------------------------------------------------------------------
        # save output parameter dictionary for saving to file
        self.pout = ParamDict()
        # get log storage keys
        storekey = self.pconstant.LOG_STORAGE_KEYS()
        # add log stats to pout
        for key in storekey:
            self.pout[storekey[key]] = []
        self.pout['LOGGER_FULL'] = []
        # add tdata_warning key
        self.pout['TDATA_WARNING'] = 1

    def __call__(self, p=None, key='', message='', printonly=False,
                 logonly=False, wrap=True, option=None, colour=None):
        """
        Function-like cal to instance of logger (i.e. WLOG)
        Parses a key (error/warning/info/graph), an option and a message to the
        stdout and the log file.

        keys are controlled by "spirouConfig.Constants.LOG_TRIG_KEYS()"
        printing to screen is controlled by "PRINT_LEVEL" constant (config.py)
        printing to log file is controlled by "LOG_LEVEL" constant (config.py)
        based on the levels described in "spirouConfig.Constants.WRITE_LEVEL"

        :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:

        :param key: string, either "error" or "warning" or "info" or graph,
                    this gives a character code in output
        :param message: string or list of strings, message to display or
                        messages to display (1 line for each message in list)
        :param printonly: bool, print only do not save to log (default = False)
        :param logonly: bool, log only do not save to log (default = False)
        :param wrap: bool, if True wraps text at
                                 spirouConfig.Constants.CHARACTER_LOG_LENGTH()
        :param option: string, option code, overwrites the default (of using
                       p['RECIPE'] or p['LOG_OPT']
        :param colour: string, colour of the message wanted (overrides default)
                       currently supported colours are:
                       "red", "green", "blue", "yellow", "cyan", "magenta",
                       "black", "white"

        output to stdout/log is as follows:

            HH:MM:SS.S - CODE |option|message

        time is output in UTC to nearest .1 seconds

        :return None:
        """
        func_name = __NAME__ + '.Logger.__call__()'

        char_len = self.pconstant.CHARACTER_LOG_LENGTH()
        # ---------------------------------------------------------------------
        # TODO: Remove deprecation warning (once all code changed)
        if type(p) is str:
            emsg = ('Need to update WLOG function call. New format required:'
                    '\n\n\tNew format: WLOG(p, level_key, message)'
                    '\n\n\tOld format: WLOG(level_key, option, message)')
            raise DeprecationWarning(emsg)
        # ---------------------------------------------------------------------
        # deal with no p and pid
        if p is None:
            p = self.pin
            p['PID'] = None
            p.set_source('PID', func_name)
            wmsg = 'Dev: Undefined PID not recommended (p is None)'
            warnings.warn(wmsg, Warning)
        # deal with no PID
        if 'PID' not in p:
            p['PID'] = None
            wmsg = 'Dev: Undefined PID not recommended (PID is missing)'
            warnings.warn(wmsg, Warning)

        # deal with no instrument
        if 'INSTRUMENT' not in p:
            p['INSTRUMENT'] = None

        # update pin and pconstant from p (selects instrument)
        self.update_param_dict(p)

        # ---------------------------------------------------------------------
        # deal with debug mode. If DRS_DEBUG is zero do not print these
        #     messages
        debug = p.get('DRS_DEBUG', 0)
        if key == 'debug' and debug == 0:
            return

        # ---------------------------------------------------------------------
        # deal with option
        if option is not None:
            option = option
        elif 'RECIPE' in p:
            option = p['RECIPE']
        elif 'LOG_OPT' in p:
            option = p['LOG_OPT']
        else:
            option = ''
        # ---------------------------------------------------------------------
        # if key is '' then set it to all
        if len(key) == 0:
            key = 'all'
        # deal with both printonly and logonly set to True (bad)
        if printonly and logonly:
            printonly, logonly = False, False
        # deal with message type (make into a list)
        if type(message) == str:
            message = [message]
        elif type(list):
            message = list(message)
        else:
            message = [('Logging error: message="{0}" is not a valid string or '
                        'list').format(message)]
            key = 'error'
        # check that key is valid
        if key not in self.pconstant.LOG_TRIG_KEYS():
            emsg = 'Logging error: key="{0}" not in LOG_TRIG_KEYS()'
            message.append(emsg.format(key))
            key = 'error'
        if key not in self.pconstant.WRITE_LEVEL():
            emsg = 'Logging error: key="{0}" not in WRITE_LEVEL()'
            message.append(emsg.format(key))
            key = 'error'
        if key not in self.pconstant.COLOUREDLEVELS():
            emsg = 'Logging error: key="{0}" not in COLOUREDLEVELS()'
            message.append(emsg.format(key))
            key = 'error'
        # loop around message (now all are lists)
        errors = []

        for mess in message:
            # Get the time now in human readable format
            human_time = time.get_time_now()
            # Get the key code (default is a whitespace)
            code = self.pconstant.LOG_TRIG_KEYS().get(key, ' ')
            # storage for cmds
            cmds = []
            # check if line is over 80 chars
            if (len(mess) > char_len) and wrap:
                # get new messages (wrapped at CHAR_LEN)
                new_messages = textwrap(mess, char_len)
                for new_message in new_messages:
                    cmdargs = [human_time, code, option, new_message]
                    cmd = '{0} - {1} |{2}|{3}'.format(*cmdargs)
                    # append separate commands for log writing
                    cmds.append(cmd)
                    # add to logger storage
                    self.logger_storage(key, human_time, new_message, printonly)
                    # print to stdout
                    if not logonly:
                        printlog(self, p, cmd, key, colour)
            else:
                cmdargs = [human_time, code, option, mess]
                cmd = '{0} - {1} |{2}|{3}'.format(*cmdargs)
                # append separate commands for log writing
                cmds.append(cmd)
                # add to logger storage
                self.logger_storage(key, human_time, mess, printonly)
                # print to stdout
                if not logonly:
                    printlog(self, p, cmd, key, colour)
            # get logfilepath
            logfilepath, warning = get_logfilepath(self, p)
            # write to log file
            if (not printonly) and (not warning):
                for cmd in cmds:
                    writelog(self, p, cmd, key, logfilepath)
            # if warning is True then we used TDATA and should report that
            if warning:
                wmsg = ('Warning "DRS_DATA_MSG" path was not found or was '
                        'missing from config. Log file not written.')
                if not logonly:
                    errors.append([wmsg, 'warning', human_time, option])

        # print any errors caused above (and set key to error to exit after)
        used = []
        for error in errors:
            if error[1] == 'error':
                key = 'error'
            if error[0] not in used:
                self.logger_storage(key, error[2], error[0])
                printlogandcmd(self, p, *error, wrap=wrap, colour=colour)
                used.append(error[0])

        # deal with errors (if key is in EXIT_LEVELS) then exit after log/print
        if key in self.pconstant.EXIT_LEVELS():
            # prepare error string
            errorstring = ''
            for mess in message:
                errorstring += mess + '\n'
            for error in errors:
                # noinspection PyTypeChecker
                errorstring += error[0] + '\n'
            # deal with debugging
            if debug:
                debug_start(self, p, errorstring)
            else:
                self.pconstant.EXIT(p)(errorstring)

    def update_param_dict(self, paramdict):
        for key in paramdict:
            # set pin value from paramdict
            self.pin[key] = paramdict[key]
            # set source from paramdict (or set to None)
            self.pin.set_source(key, paramdict.sources.get(key, None))
            # update instrument and pconstant
            self.instrument = paramdict['INSTRUMENT']
            self.pconstant = constants.pload(self.instrument)

    def output_param_dict(self, paramdict):
        for key in self.pout:
            # get value
            value = self.pout[key]
            # set value from pout (make sure it is copied)
            paramdict[key] = type(value)(value)
            # set source from pout
            paramdict.set_source(key, self.pout.sources.get(key, None))
        # return paramdict
        return paramdict

    def logger_storage(self, key, ttime, mess, printonly=False):
        if printonly:
            return 0
        # get log storage keys
        storekey = self.pconstant.LOG_STORAGE_KEYS()
        # find if key is defined in storage
        if key in storekey:
            # if key is in LOG just append message to list
            if storekey[key] in self.pout:
                self.pout[storekey[key]].append([ttime, mess])
            # if key isn't in LOG make new list (for future append)
            else:
                self.pout[storekey[key]] = [[ttime, mess]]
        # add to full log
        self.pout['LOGGER_FULL'].append([[ttime, mess]])

    def clean_log(self, processid):
        # get log storage keys
        storekey = self.pconstant.LOG_STORAGE_KEYS()
        # clean out for this ID
        self.pout[processid] = ParamDict()
        # populate log keys
        for key in storekey:
            self.pout[processid][storekey[key]] = []
        self.pout[processid]['LOGGER_FULL'] = []


# =============================================================================
# Define our instance of wlog
# =============================================================================
# Get our instance of logger
wlog = Logger()


# =============================================================================
# Define functions
# =============================================================================
def printlogandcmd(logobj, p, message, key, human_time, option, wrap, colour):
    """
    Prints log to standard output/screen (for internal use only when
    logger cannot be used)

        output to stdout is as follows:

        HH:MM:SS.S - CODE |option|message

    :param logobj: logger instance, the logger object (for pconstant)
    :param p: ParamDict, the constants file passed from call
    :param message: string, the message of the printed output
    :param key: string, the CODE key for the printed output
    :param human_time: string, the human time for the printed output
    :param option: string, the option of the output
    :param wrap: bool, if True wraps tet to CHAR_LEN (defined in
                 spirouConfig.Constants.CHARACTER_LOG_LENGTH())
    :param colour: string, colour of the message wanted (overrides default)
                   currently supported colours are:
                   "red", "green", "blue", "yellow", "cyan", "magenta",
                   "black", "white"

    :return None:
    """
    # get character log length
    char_len = logobj.pconstant.CHARACTER_LOG_LENGTH()
    # deal with string message (force to list)
    if type(message) == str:
        message = [message]
    elif type(list):
        message = list(message)
    else:
        message = [('Logging error: message="{0}" is not a valid string or '
                    'list').format(message)]
        key = 'error'
    for mess in message:
        code = logobj.pconstant.LOG_TRIG_KEYS().get(key, ' ')
        # check if line is over 80 chars
        if (len(mess) > char_len) and wrap:
            # get new messages (wrapped at CHAR_LEN)
            new_messages = textwrap(mess, char_len)
            for new_message in new_messages:
                cmdargs = [human_time, code, option, new_message]
                cmd = '{0} - {1} |{2}|{3}'.format(*cmdargs)
                printlog(logobj, p, cmd, key, colour)
        else:
            cmdargs = [human_time, code, option, mess]
            cmd = '{0} - {1} |{2}|{3}'.format(*cmdargs)
            printlog(logobj, p, cmd, key, colour)


def debug_start(logobj, p, errorstring):
    """
    Initiate debugger (for DEBUG mode) - will start when an error is raised
    if 'DRS_DEBUG' is set to True or 1 (in config.py)

    :param logobj: logger instance, the logger object (for pconstant)
    :param errorstring: string, the error to pipe to Sys.Exit after
                        debugging options selected

    uses pdb to do python debugging

    Asks user [Y]es or [N]o to debugging then exits on 'N' or after debugger
    is quit

    :return None:
    """
    # get raw input
    if sys.version_info.major > 2:
        # noinspection PyPep8
        raw_input = lambda x: str(input(x))
    # get colour
    clevels = logobj.pconstant.COLOUREDLEVELS()
    addcolour = p['DRS_COLOURED_LOG']

    nocol = Color.ENDC
    if addcolour:
        cc = clevels['error']
    else:
        cc = nocol
    # ask to run debugger
    # noinspection PyBroadException
    try:
        print(cc + '\n\n\tError found and running in DEBUG mode\n' + nocol)
        # noinspection PyUnboundLocalVariable
        message = ('Enter (1) ipython debugger (2) python debugger or '
                   'exit (any other key)?\n\t Note ipython debugger requires '
                   'ipdb installed\n\tChoose "1", "2", or exit:')

        # noinspection PyUnboundLocalVariable
        uinput = raw_input(cc + '\t' + message + '\t' + nocol)
        if '1' in uinput.upper():
            print(cc + '\n\t ==== IPYTHON DEBUGGER ====\n'
                       '\n\t - type "ipython()" to use %paste %cpaste'
                       '\n\t - type "list" to list code'
                       '\n\t - type "up" to go up a level'
                       '\n\t - type "interact" to go to an interactive shell'
                       '\n\t - type "print(variable)" to print variable'
                       '\n\t - type "print(dir())" to list available variables'
                       '\n\t - type "continue" to exit'
                       '\n\t - type "help" to see all commands'
                       '\n\n\t ==================\n\n' + nocol)

            # noinspection PyBroadException
            try:
                from IPython import embed
                # noinspection PyUnboundLocalVariable
                ipython = embed
                import ipdb
                ipdb.set_trace()
            except:
                import pdb
                pdb.set_trace()

            print(cc + '\n\nCode Exited' + nocol)
            logobj.pconstant.EXIT(p)(errorstring)
        if '2' in uinput.upper():
            print(cc + '\n\t ==== DEBUGGER ====\n'
                       '\n\t - type "list" to list code'
                       '\n\t - type "up" to go up a level'
                       '\n\t - type "interact" to go to an interactive shell'
                       '\n\t - type "print(variable)" to print variable'
                       '\n\t - type "print(dir())" to list available variables'
                       '\n\t - type "continue" to exit'
                       '\n\t - type "help" to see all commands'
                       '\n\n\t ==================\n\n' + nocol)

            import pdb
            pdb.set_trace()

            print(cc + '\n\nCode Exited' + nocol)
            logobj.pconstant.EXIT(p)(errorstring)
        else:
            logobj.pconstant.EXIT(p)(errorstring)
    except:
        logobj.pconstant.EXIT(p)(errorstring)


def warninglogger(p, w, funcname=None):
    """
    Warning logger - takes "w" - a list of caught warnings and pipes them on
    to the log functions. If "funcname" is not None then t "funcname" is
    printed with the line reference (intended to be used to identify the code/
    function/module warning was generated in)

    to catch warnings use the following:

    >> import warnings
    >> with warnings.catch_warnings(record=True) as w:
    >>     code_to_generate_warnings()
    >> warninglogger(w, 'some name for logging')

    :param p: ParamDict, the constants dictionary passed in call
    :param w: list of warnings, the list of warnings from
               warnings.catch_warnings
    :param funcname: string or None, if string then also pipes "funcname" to the
                     warning message (intended to be used to identify the code/
                     function/module warning was generated in)
    :return:
    """
    # deal with warnings
    displayed_warnings = []
    if p['LOG_CAUGHT_WARNINGS'] and (len(w) > 0):
        for wi in w:
            # if we have a function name then use it else just report the
            #    line number (not recommended)
            if funcname is None:
                wargs = [wi.lineno, '', wi.message]
            else:
                wargs = [wi.lineno, '({0})'.format(funcname), wi.message]

            # log message
            wmsg = 'python warning Line {0} {1} warning reads: {2}'
            wmsg = wmsg.format(*wargs)
            # if we have already display this warning don't again
            if wmsg in displayed_warnings:
                continue
            else:
                wlog(p, 'warning', wmsg)
                displayed_warnings.append(wmsg)


def get_logfilepath(logobj, p):
    """
    Construct the log file path and filename (normally from "DRS_DATA_MSG" but
    if this is not defined/not found then defaults to "TDATA"/msg or generates
    an ConfigError exception.

    "DRS_DATA_MSG" and "TDATA" are defined in "config.py"

    :return lpath: string, the path and filename for the log file to be used
    :return warning: bool, if True then "TDATA" was used instead of "DRS_DATA
    """
    msgkey = 'DRS_DATA_MSG'
    # -------------------------------------------------------------------------
    # Get DRS_DATA_MSG folder directory
    dir_data_msg = p.get(msgkey, None)
    # if None use "TDATA"
    if dir_data_msg is None:
        emsg1 = 'Fatal error: Cannot write to log file.'
        emsg2 = '\t"{0}" missing from config'.format(msgkey)
        warnings.warn(emsg1 + '\n' + emsg2, Warning)
        warning = True
    # if it doesn't exist also set to TDATA
    elif not os.path.exists(dir_data_msg):
        emsg1 = 'Fatal error: Cannot write to log file.'
        emsg2 = ' "{0}" does not exist.'.format(msgkey)
        emsg3 = '    "{0}" = {1}'.format(msgkey, p[msgkey])
        warnings.warn(emsg1 + '\n' + emsg2 + '\n' + emsg3, Warning)
        warning = True
    else:
        warning = False
    # do not save to log file
    if warning:
        return None, warning
    else:
        lpath = logobj.pconstant.LOG_FILE_NAME(p, dir_data_msg)
        # return the logpath and the warning
        return lpath, warning


def correct_level(logobj, key, level):
    """
    Decides (based on WRITE_LEVEL) whether this level ("key") is to be printed/
    logged (based on the level "level"), return True if we should log key based
    on level. Returns True if: thislevel >= outlevel  else False
         where:
            thislevel = SpirouConfig.SpirouConst.WRITE_LEVEL()[key]
            outlevel = SpirouConfig.SpirouConst.WRITE_LEVEL()[level]

    :param logobj: logger instance, the logger object (for pconstant)
    :param key: string, test key (must be in
                SpirouConfig.SpirouConst.LOG_TRIG_KEYS() and
                SpirouConfig.SpirouConst.WRITE_LEVEL()
    :param level: string, write key (must be in
                SpirouConfig.SpirouConst.LOG_TRIG_KEYS() and
                SpirouConfig.SpirouConst.WRITE_LEVEL()

    :return test: bool, True if: thislevel >= outlevel  else False
                    where:

                    thislevel = SpirouConfig.SpirouConst.WRITE_LEVEL()[key]
                    outlevel = SpirouConfig.SpirouConst.WRITE_LEVEL()[level]

    """
    func_name = __NAME__ + '.correct_level()'
    # get numeric value for out level
    try:
        outlevel = logobj.pconstant.WRITE_LEVEL()[level]
    except KeyError:
        emsg1 = '"level"={0} not in SpirouConfig.SpirouConst.WRITE_LEVEL()'
        emsg2 = '   function = {0}'.format(func_name)
        raise ConfigError(message=[emsg1.format(level), emsg2], level='error')

    # get numeric value for this level
    try:
        thislevel = logobj.pconstant.WRITE_LEVEL()[key]
    except KeyError:
        emsg1 = '"key"={0} not in SpirouConfig.SpirouConst.WRITE_LEVEL()'
        emsg2 = '   function = {0}'.format(func_name)
        raise ConfigError(message=[emsg1.format(key), emsg2], level='error')

    # return whether we are printing or not
    return thislevel >= outlevel


def printlog(logobj, p, message, key='all', colour=None):
    """
    print message to stdout (if level is correct - set by PRINT_LEVEL)
    is coloured unless spirouConfig.Constants.COLOURED_LOG() is False

    :param logobj: logger instance, the logger object (for pconstant)
    :param p: ParamDict, the constants file passed in call
    :param message: string, the formatted log line to write to stdout
    :param key: string, either "error" or "warning" or "info" or "graph" or
                "all", this gives a character code in output
    :param colour: string, colour of the message wanted (overrides default)
                   currently supported colours are:
                   "red", "green", "blue", "yellow", "cyan", "magenta",
                   "black", "white"

    :return None:
    """
    func_name = __NAME__ + '.printlog()'
    # get the colours for the "key"
    c1, c2 = printcolour(logobj, p, key, func_name=func_name, colour=colour)
    # if the colours are not None then print the message
    if c1 is not None and c2 is not None:
        print(c1 + message + c2)


def textwrap(input_string, length):
    # Modified version of this: https://stackoverflow.com/a/16430754
    new_string = []
    for s in input_string.split("\n"):
        if s == "":
            new_string.append('')
        wlen = 0
        line = []
        for dor in s.split():
            if wlen + len(dor) + 1 <= length:
                line.append(dor)
                wlen += len(dor) + 1
            else:
                new_string.append(" ".join(line))
                line = [dor]
                wlen = len(dor)
        if len(line):
            new_string.append(" ".join(line))

    # add a tab to all but first line
    new_string2 = [new_string[0]]
    for it in range(1, len(new_string)):
        new_string2.append('\t' + new_string[it])

    return new_string2


def printcolour(logobj, p, key='all', func_name=None, colour=None):
    """
    Get the print colour (start and end) based on "key".
    This should be used as follows:
        >> c1, c2 = printcolour(key='all')
        >> print(c1 + message + c2)

    :param logobj: logger instance, the logger object (for pconstant)
    :param p: ParamDict, the constants file passed in call
    :param key: string, either "error" or "warning" or "info" or "graph" or
                "all", this gives a character code in output
    :param func_name: string or None, if not None then defines the function to
                      report in the error
    :param colour: string, colour of the message wanted (overrides default)
                   currently supported colours are:
                   "red", "green", "blue", "yellow", "cyan", "magenta",
                   "black", "white"

    :return colour1: string or None, if key is found and we are using coloured
                     log returns the starting colour, if not returns empty
                     string if key is not accepted does not print
    :return colour2: string or None, if key is found and we are using coloured
                     log returns the ending colour, if not returns empty
                     string if key is not accepted does not print
    """
    if func_name is None:
        func_name = __NAME__ + '.printcolour()'
    # get out level key
    level = p.get('PRINT_LEVEL', 'all')
    # deal with overriding coloured text
    if colour is not None:
        colour1, colour2 = override_colour(p, colour)
        if colour1 is not None:
            return colour1, colour2
    # get the colours
    clevels = logobj.pconstant.COLOUREDLEVELS(p)
    addcolour = p['DRS_COLOURED_LOG']
    nocol = Color.ENDC
    # make sure key is in clevels
    if (key not in clevels) and addcolour:
        emsg1 = 'key={0} not in spirouConfig.Constants.COLOUREDLEVELS()'
        emsg2 = '    function = {0}'.format(func_name)
        raise ConfigError(message=[emsg1.format(key), emsg2], level='error')
    # if this level is greater than or equal to out level then print to stdout
    if correct_level(logobj, key, level) and (key in clevels) and addcolour:
        colour1 = clevels[key]
        colour2 = nocol
    elif correct_level(logobj, key, level):
        colour1 = ''
        colour2 = ''
    else:
        colour1, colour2 = None, None
    # return colour1 and colour2
    return colour1, colour2


def override_colour(p, colour):
    """
    Override the colour with the themed colours

    :param p: ParamDict, the constants file passed in call
    :param colour: string, colour of the message wanted (overrides default)
                   currently supported colours are:
                   "red", "green", "blue", "yellow", "cyan", "magenta",
                   "black", "white"
    :return colour1: string or None, if key is found and we are using coloured
                     log returns the starting colour, if not returns empty
                     string if key is not accepted does not print
    :return colour2: string or None, if key is found and we are using coloured
                     log returns the ending colour, if not returns empty
                     string if key is not accepted does not print
    """

    # get the colour codes
    codes = Color
    # get theme
    if 'THEME' not in p:
        theme = 'DARK'
    else:
        theme = p['THEME']
    # get colour 1
    if theme == 'DARK':
        # find colour 1 in colour
        if colour.lower() == "red":
            colour1 = codes.RED1
        elif colour.lower() == "green":
            colour1 = codes.GREEN1
        elif colour.lower() == "blue":
            colour1 = codes.BLUE1
        elif colour.lower() == "yellow":
            colour1 = codes.YELLOW1
        elif colour.lower() == "cyan":
            colour1 = codes.CYAN1
        elif colour.lower() == "magenta":
            colour1 = codes.MAGENTA1
        elif colour.lower() == 'black':
            colour1 = codes.BLACK1
        elif colour.lower() == 'white':
            colour1 = codes.WHITE1
        else:
            colour1 = None
    # get colour 1
    else:
        # find colour 1 in colour
        if colour.lower() == "red":
            colour1 = codes.RED2
        elif colour.lower() == "green":
            colour1 = codes.GREEN2
        elif colour.lower() == "blue":
            colour1 = codes.BLUE2
        elif colour.lower() == "yellow":
            colour1 = codes.YELLOW2
        elif colour.lower() == "cyan":
            colour1 = codes.CYAN2
        elif colour.lower() == "magenta":
            colour1 = codes.MAGENTA2
        elif colour.lower() == 'black':
            colour1 = codes.BLACK2
        elif colour.lower() == 'white':
            colour1 = codes.WHITE2
        else:
            colour1 = None
    # last code should be the end
    colour2 = codes.ENDC
    # return colour1 and colour2
    return colour1, colour2


def writelog(logobj, p, message, key, logfilepath):
    """
    write message to log file (if level is correct - set by LOG_LEVEL)

    :param logobj: logger instance, the logger object (for pconstant)
    :param p: ParamDict, the constants file passed in call
    :param message: string, message to write to log file
    :param key: string, either "error" or "warning" or "info" or graph, this
                gives a character code in output

    :param logfilepath: string, the file name to write the log to

    :return:
    """
    func_name = __NAME__ + '.writelog()'
    # -------------------------------------------------------------------------
    # get out level key
    level = p.get('LOG_LEVEL', 'all')
    # if this level is less than out level then do not log
    if not correct_level(logobj, key, level):
        return 0
    # -------------------------------------------------------------------------
    # Check if logfile path exists
    if os.path.exists(logfilepath):
        # try to open the logfile
        try:
            # open/write and close the logfile
            f = open(logfilepath, 'a')
            f.write(message + '\n')
            f.close()
        except Exception as e:
            emsg1 = 'Cannot open {0}, error was: {1}'
            emsg2 = '   function = {0}'.format(func_name)
            raise ConfigError(message=[emsg1.format(logfilepath, e), emsg2])
    else:
        # try to open the logfile
        try:
            # open/write and close the logfile
            f = open(logfilepath, 'a')
            # write the first message line
            f.write(message + '\n')
            f.close()
            try:
                # change mode to rw-rw-rw-
                os.chmod(logfilepath, 0o666)
            # Pass over all OS Errors
            except OSError:
                pass
        # If we cannot write to log file then print to stdout
        except Exception as e:
            emsg1 = 'Cannot open {0}, error was: {1}'
            emsg2 = '   function = {0}'.format(func_name)
            raise ConfigError(message=[emsg1.format(logfilepath, e), emsg2])


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get fake p
    pp = ParamDict()
    pp['PID'] = None
    pp['RECIPE'] = ''

    # Get Logging function
    WLOG = wlog
    # Title test
    WLOG(pp, '', ' *****************************************')
    WLOG(pp, '', ' * TEST @(#) Some Observatory (' + 'V0.0.-1' + ')')
    WLOG(pp, '', ' *****************************************')
    # info log
    WLOG(pp, 'info', "This is an info test")
    # warning log
    WLOG(pp, 'warning', "This is a warning test")
    # error log
    WLOG(pp, 'error', "This is an error test")

# =============================================================================
# End of code
# =============================================================================

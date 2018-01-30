#!/usr/bin/env python3
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
import time
import os
import sys

from SpirouDRS import spirouConfig
from . import spirouMath

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouLog.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# -----------------------------------------------------------------------------
# Get constant parameters
CPARAMS = spirouConfig.ReadConfigFile()
TRIG_KEY = spirouConfig.Constants.LOG_TRIG_KEYS()
WRITE_LEVEL = spirouConfig.Constants.WRITE_LEVEL()
EXIT_TYPE = spirouConfig.Constants.EXIT()
EXIT_LEVELS = spirouConfig.Constants.EXIT_LEVELS()
# Boolean for whether we log caught warnings
WARN = spirouConfig.Constants.LOG_CAUGHT_WARNINGS()
# Get the Config error
ConfigError = spirouConfig.ConfigError
# Constant for warning about using tdata
TDATA_WARNING = 1


# =============================================================================
# Define functions
# =============================================================================
def logger(key='', option='', message=''):
    """
    Parses a key (error/warning/info/graph), an option and a message to the
    stdout and the log file.

    keys are controlled by "spirouConfig.Constants.LOG_TRIG_KEYS()"
    printing to screen is controlled by "PRINT_LEVEL" constant (config.py)
    printing to log file is controlled by "LOG_LEVEL" constant (config.py)
    based on the levels described in "spirouConfig.Constants.WRITE_LEVEL"

    :param key: string, either "error" or "warning" or "info" or graph, this
                gives a character code in output
    :param option: string, option code
    :param message: string or list of strings, message to display or messages
                    to display (1 line for each message in list)

    output to stdout/log is as follows:

        HH:MM:SS.S - CODE |option|message

    time is output in UTC to nearest .1 seconds

    :return:
    """
    # allow tdata_warning to be changed
    global TDATA_WARNING
    # if key is '' then set it to all
    if len(key) == 0:
        key = 'all'

    if type(message) == str:
        message = [message]
    elif type(list):
        message = list(message)
    else:
        message = [('Logging error: message="{0}" is not a valid string or '
                    'list').format(message)]
        key = 'error'
    # loop around message (now all are lists)
    for mess in message:
        # get the time format and display time zone from constants
        tfmt = spirouConfig.Constants.LOG_TIME_FORMAT()
        zone = spirouConfig.Constants.LOG_TIMEZONE()
        # Get the time now in human readable format
        unix_time = spirouMath.get_time_now_unix(zone=zone)
        human_time = spirouMath.get_time_now_string(fmt=tfmt, zone=zone)

        # Get the first decimal part of the unix time
        dsec = int((unix_time - int(unix_time)) * 10)
        # Get the key code (default is a whitespace)
        code = TRIG_KEY.get(key, ' ')
        # construct the log and log error
        cmdargs = [human_time, dsec, code, option, mess]
        cmd = '{0}.{1:1d} - {2} |{3}|{4}'.format(*cmdargs)
        ecmd = '{0}.{1:1d} - {2} |{3}|NOT IN LOGS: {4}'.format(*cmdargs)
        # print to stdout
        printlog(cmd, key)
        # get logfilepath
        try:
            logfilepath, warning = get_logfilepath(unix_time)
            # write to log file
            writelog(cmd, ecmd, key, logfilepath)
        except ConfigError as e:
            printlogandcmd(e.message, e.level, human_time, dsec, option)
            warning = False
            key = 'error'
        # if warning is True then we used TDATA and should report that
        if warning and TDATA_WARNING:
            wmsg = ('Warning "DRS_DATA_MSG" path was not found, using '
                    'path "TDATA"={0}')
            printlogandcmd(wmsg.format(CPARAMS.get('TDATA', '')), 'warning',
                           human_time, dsec, option)
            TDATA_WARNING = 0

    # deal with errors (if key is in EXIT_LEVELS) then exit after log/print
    if key in EXIT_LEVELS:
        if spirouConfig.Constants.DEBUG():
            debug_start()
        else:
            EXIT_TYPE(1)


def printlogandcmd(message, key, human_time, dsec, option):
    """
    Prints log to standard output/screen (for internal use only when
    logger cannot be used)

        output to stdout is as follows:

        HH:MM:SS.S - CODE |option|message

    :param message: string, the message of the printed output
    :param key: string, the CODE key for the printed output
    :param human_time: string, the human time for the printed output
    :param dsec: float, the "tenth of a second" output
    :param option: string, the option of the output

    :return None:
    """
    if type(message) == str:
        message = [message]
    elif type(list):
        message = list(message)
    else:
        message = [('Logging error: message="{0}" is not a valid string or '
                    'list').format(message)]
        key = 'error'
    for mess in message:
        code = TRIG_KEY.get(key, ' ')
        cmdargs = [human_time, dsec, code, option, mess]
        cmd = '{0}.{1:1d} - {2} |{3}|{4}'.format(*cmdargs)
        printlog(cmd, key)


def debug_start():
    """
    Initiate debugger (for DEBUG mode) - will start when an error is raised
    if 'DRS_DEBUG' is set to True or 1 (in config.py)

    uses pdb to do python debugging

    Asks user [Y]es or [N]o to debugging then exits on 'N' or after debugger
    is quit

    :return None:
    """
    # get raw input
    if sys.version_info.major > 2:
        raw_input = lambda x: str(input(x))
    # get colour
    clevels = spirouConfig.Constants.COLOUREDLEVELS()
    addcolour = spirouConfig.Constants.COLOURED_LOG()
    nocol = spirouConfig.Constants.bcolors.ENDC
    if addcolour:
        cc = clevels['error']
    else:
        cc = nocol
    # ask to run debugger
    try:
        print(cc + '\n\n\tError found and running in DEBUG mode\n' + nocol)
        uinput = raw_input(cc + '\tEnter python debugger? [Y]es or [N]o?\t'
                           + nocol)
        if 'Y' in uinput.upper():
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
            EXIT_TYPE(1)
        else:
            EXIT_TYPE(1)
    except :
        EXIT_TYPE(1)


def warninglogger(w, funcname=None):
    """
    Warning logger - takes "w" - a list of caught warnings and pipes them on
    to the log functions. If "funcname" is not None then t "funcname" is
    printed with the line reference (intended to be used to identify the code/
    function/module warning was generated in)

    to catch warnings use the following:

    >>> with warnings.catch_warnings(record=True) as w:
    >>>     code_to_generate_warnings()
    >>> warninglogger(w, 'some name for logging')

    :param w: list of warnings, the list of warnings from
               warnings.catch_warnings
    :param funcname: string or None, if string then also pipes "funcname" to the
                     warning message (intended to be used to identify the code/
                     function/module warning was generated in)
    :return:
    """
    # deal with warnings
    if WARN and (len(w) > 0):
        for wi in w:
            # if we have a function name then use it else just report the
            #    line number (not recommended)
            if funcname is None:
                wargs = [wi.lineno, '', wi.message]
            else:
                wargs = [wi.linno, '({0})'.format(funcname), wi.message]
            # log message
            wmsg = 'python warning Line {0} {1} warning reads: {2}'
            logger('warning', wmsg.format(*wargs))


def get_logfilepath(utime):
    """
    Construct the log file path and filename (normally from "DRS_DATA_MSG" but
    if this is not defined/not found then defaults to "TDATA"/msg or generates
    an ConfigError exception.

    "DRS_DATA_MSG" and "TDATA" are defined in "config.py"

    :param utime: float, the unix time to add to the log file filename.

    :return lpath: string, the path and filename for the log file to be used
    :return warning: bool, if True then "TDATA" was used instead of "DRS_DATA
    """
    msgkey, tkey = 'DRS_DATA_MSG', 'TDATA'
    # -------------------------------------------------------------------------
    # Get DRS_DATA_MSG folder directory
    dir_data_msg = CPARAMS.get(msgkey, None)
    # if None use "TDATA"
    if dir_data_msg is None:
        warning = True
        dir_data_msg = CPARAMS.get(tkey, None)
        # check that it exists
        if not os.path.exists(dir_data_msg):
            emsg1 = 'Fatal error: Cannot write to log file.'
            emsg2 = (' "{0}" missing from config AND "{1}" directory'
                     ' does not exist.').format(msgkey, tkey)
            emsg3 = '    "{0}" = {1}'.format(msgkey, CPARAMS.get(msgkey, ''))
            emsg4 = '    "{0}" = {1}'.format(tkey, CPARAMS.get(tkey, ''))
            raise ConfigError(message=[emsg1, emsg2, emsg3, emsg4],
                              level='error')
    # if it doesn't exist also set to TDATA
    elif not os.path.exists(dir_data_msg):
        warning = True
        dir_data_msg = CPARAMS.get(tkey, None)
        # check that it exists
        if not os.path.exists(dir_data_msg):
            emsg1 = 'Fatal error: Cannot write to log file.'
            emsg2 = (' "{0}" AND "{1}" directories'
                     ' do not exist.').format(msgkey, tkey)
            emsg3 = '    "{0}" = {1}'.format(msgkey, CPARAMS.get(msgkey, ''))
            emsg4 = '    "{0}" = {1}'.format(tkey, CPARAMS.get(tkey, ''))
            raise ConfigError(message=[emsg1, emsg2, emsg3, emsg4],
                              level='error')
    else:
        warning = False
    # -------------------------------------------------------------------------
    # if still None then TDATA does not exist in config file
    if dir_data_msg is None:
        emsg1 = 'Fatal error: Cannot write to log file.'
        emsg2 = ('   "{0}" and "{1}" are missing from the config file'
                 '').format(msgkey, tkey)
        emsg3 = '    "{0}" = {1}'.format(msgkey, CPARAMS.get(msgkey, ''))
        emsg4 = '    "{0}" = {1}'.format(tkey, CPARAMS.get(tkey, ''))
        raise ConfigError(message=[emsg1, emsg2, emsg3, emsg4], level='error')
    # if we are using TDATA need to create msg folder
    elif warning:
        dir_data_msg = os.path.join(dir_data_msg, 'msg', '')
        # make directory
        try:
            os.makedirs(dir_data_msg, exist_ok=True)
        except Exception as e:
            emsg = 'Fatal error: cannot create folder {0} error {1}: {2}'
            raise ConfigError(message=emsg.format(dir_data_msg, type(e), e),
                              level='error')

    # Get the used date if it is not None
    CPARAMS['DRS_USED_DATE'] = CPARAMS.get('DRS_USED_DATE', 'None').upper()
    udate = CPARAMS['DRS_USED_DATE']
    if udate == 'undefined' or udate == 'NONE':
        date = time.strftime('%Y-%m-%d', time.gmtime(utime - 43200))
    else:
        date = CPARAMS['DRS_USED_DATE']
    # Get the HOST name (if it does not exist host = 'HOST')
    host = os.environ.get('HOST', 'HOST')
    # construct the logfile path
    lpath = os.path.join(dir_data_msg, 'DRS-{0}.{1}'.format(host, date))
    # return the logpath and the warning
    return lpath, warning


def correct_level(key, level):
    """
    Decides (based on WRITE_LEVEL) whether this level ("key") is to be printed/
    logged (based on the level "level"), return True if we should log key based
    on level. Returns True if: thislevel >= outlevel  else False
         where:
            thislevel = SpirouConfig.SpirouConst.WRITE_LEVEL()[key]
            outlevel = SpirouConfig.SpirouConst.WRITE_LEVEL()[level]

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
        outlevel = WRITE_LEVEL[level]
    except KeyError:
        emsg1 = '"level"={0} not in SpirouConfig.SpirouConst.WRITE_LEVEL()'
        emsg2 = '   function = {0}'.format(func_name)
        raise ConfigError(message=[emsg1.format(level), emsg2], level='error')

    # get numeric value for this level
    try:
        thislevel = WRITE_LEVEL[key]
    except KeyError:
        emsg1 = '"key"={0} not in SpirouConfig.SpirouConst.WRITE_LEVEL()'
        emsg2 = '   function = {0}'.format(func_name)
        raise ConfigError(message=[emsg1.format(key), emsg2], level='error')

    # return whether we are printing or not
    return thislevel >= outlevel


def printlog(message, key):
    """
    print message to stdout (if level is correct - set by PRINT_LEVEL)

    :param message: string, the formatted log line to write to stdout
    :param key: string, either "error" or "warning" or "info" or graph, this
                gives a character code in output
    :return:
    """
    func_name = __NAME__ + '.printlog()'
    # get out level key
    level = CPARAMS.get('PRINT_LEVEL', 'all')
    clevels = spirouConfig.Constants.COLOUREDLEVELS()
    addcolour = spirouConfig.Constants.COLOURED_LOG()
    nocol = spirouConfig.Constants.bcolors.ENDC
    # make sure key is in clevels
    if (key not in clevels) and addcolour:
        emsg1 = 'key={0} not in spirouConfig.Constants.COLOUREDLEVELS()'
        emsg2 = '    function = {0}'.format(func_name)
        raise ConfigError(message=[emsg1.format(key), emsg2], level='error')

    # if this level is greater than or equal to out level then print to stdout
    if correct_level(key, level) and (key in clevels) and addcolour:
        print(clevels[key] + message + nocol)
    elif correct_level(key, level):
        print(message)


def writelog(message, errormessage, key, logfilepath):
    """
    write message to log file (if level is correct - set by LOG_LEVEL)

    :param message: string, message to write to log file
    :param errormessage: string, error message to print to stdout if we cannot
                         write to log file
    :param key: string, either "error" or "warning" or "info" or graph, this
                gives a character code in output

    :param logfilepath: string, the file name to write the log to

    :return:
    """
    func_name = __NAME__ + '.writelog()'
    # -------------------------------------------------------------------------
    # get out level key
    level = CPARAMS.get('LOG_LEVEL', 'all')
    # if this level is less than out level then do not log
    if not correct_level(key, level):
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
    dprog = spirouConfig.Constants.DEFAULT_LOG_OPT()
    # Title test
    logger('', '', ' *****************************************')
    logger('', '', ' * TEST @(#) Some Observatory (' + 'V0.0.-1' + ')')
    logger('', '', ' *****************************************')
    # info log
    logger("info", dprog, "This is an info test")
    # warning log
    logger("warning", dprog, "This is a warning test")
    # error log
    logger("error", dprog, "This is an error test")

# =============================================================================
# End of code
# =============================================================================

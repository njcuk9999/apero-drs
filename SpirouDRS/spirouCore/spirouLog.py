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

import time
import os
import sys

from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouLog.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# -----------------------------------------------------------------------------
# Get constant parameters
CPARAMS = spirouConfig.ReadConfigFile()
TRIG_KEY = spirouConfig.Constants.LOG_TRIG_KEYS()
WRITE_LEVEL = spirouConfig.Constants.WRITE_LEVEL()
EXIT = spirouConfig.Constants.LOG_EXIT_TYPE()
# Boolean for whether we log caught warnings
WARN = spirouConfig.Constants.LOG_CAUGHT_WARNINGS()
# -----------------------------------------------------------------------------
# Config exit (sys = sys.exit(1), os = os._exit(1) anything else and error
#     does not exit
# TODO: should this be defined in the config?
if EXIT == 'sys':
    EXIT_TYPE = sys.exit
elif EXIT == 'os':
    EXIT_TYPE = os._exit
else:
    EXIT_TYPE = lambda x: None



# =============================================================================
# Define functions
# =============================================================================
def logger(key='', option='', message=''):
    """
    Parses a key (error/warning/info/graph), an option and a message to the
    stdout and the log file

    :param key: string, either "error" or "warning" or "info" or graph, this
                gives a character code in output
    :param option: string, option code
    :param message: string, message to display

    output to stdout/log is as follows:

    HH:MM:SS.S - CODE |option|message

    time is output in UTC to nearest .1 seconds

    :return:
    """
    # if key is '' then set it to all
    if len(key) == 0:
        key = 'all'
    # Get the local unix time now
    unix_time = time.time()
    # Get the UTC time now in human readable format
    human_time = time.strftime('%H:%M:%S', time.gmtime(unix_time))
    # Get the first decimal part of the unix time
    dsec = int((unix_time - int(unix_time)) * 10)
    # Get the key code (default is a whitespace)
    code = TRIG_KEY.get(key, ' ')
    # construct the log and log error
    cmdargs = [human_time, dsec, code, option, message]
    cmd = '{0}.{1:1d} - {2} |{3}|{4}'.format(*cmdargs)
    ecmd = '{0}.{1:1d} - {2} |{3}|NOT IN LOGS: {4}'.format(*cmdargs)
    # print to stdout
    printlog(cmd, key)
    # get logfilepath
    logfilepath = get_logfilepath(unix_time)
    # write to log file
    writelog(cmd, ecmd, key, logfilepath)
    # deal with errors
    if key == 'error':
        EXIT_TYPE(1)


def warninglogger(w):
    # deal with warnings
    if WARN and (len(w) > 0):
        for wi in w:
            wargs = [wi.lineno, wi.message]
            logger('warning', 'python warning',
                   'Line {0} warning reads: {1}'.format(*wargs))


def get_logfilepath(utime):
    # -------------------------------------------------------------------------
    # Get DRS_DATA_MSG folder directory
    dir_data_msg = CPARAMS.get('DRS_DATA_MSG', '')
    # check that DRS_DATA_MSG path exists
    if not os.path.exists(dir_data_msg):
        # if TDATA path does not exists - exit with error
        if not os.path.exists(CPARAMS.get('TDATA', '')):
            print(spirouConfig.Constants.CONFIG_KEY_ERROR('TDATA'))
            EXIT_TYPE(1)
        # if TDATA does exist then create a /msg/ sub-directory
        dir_data_msg = os.path.join(CPARAMS['TDATA'], 'msg', '')
        os.makedirs(dir_data_msg)
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
    return os.path.join(dir_data_msg, 'DRS-{0}.{1}'.format(host, date))


def printlog(message, key):
    """
    print message to stdout (if level is correct - set by PRINT_LEVEL)

    :param message: string, the formatted log line to write to stdout
    :param key: string, either "error" or "warning" or "info" or graph, this
                gives a character code in output
    :return:
    """
    # get out level key
    level = CPARAMS.get('PRINT_LEVEL', 'all')
    # get numeric value for out level
    outlevel = WRITE_LEVEL[level]
    # get numeric value for this level
    thislevel = WRITE_LEVEL[key]
    # if this level is greater than or equal to out level then print to stdout
    if thislevel >= outlevel:
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
    # -------------------------------------------------------------------------
    # get out level key
    level = CPARAMS.get('PRINT_LEVEL', 'all')
    # get numeric value for out level
    outlevel = WRITE_LEVEL[level]
    # get numeric value for this level
    thislevel = WRITE_LEVEL[key]
    # if this level is less than out level then do not log
    if thislevel < outlevel:
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
        except IOError:
            # TODO: This could be changed to printlog(...)
            print(errormessage)
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
        except IOError:
            # TODO: This could be changed to printlog(...)
            print(errormessage)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Title test
    logger('', '', ' *****************************************')
    logger('', '', ' * TEST @(#) Some Observatory (' + 'V0.0.1' + ')')
    logger('', '', ' *****************************************')
    # info log
    logger("info", "-c:", "This is an info test")
    # warning log
    logger("warning", "-c:", "This is a warning test")
    # error log
    logger("error", "-c:", "This is an error test")

# =============================================================================
# End of code
# =============================================================================

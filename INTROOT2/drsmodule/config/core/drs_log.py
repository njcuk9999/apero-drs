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
import numpy as np
import os
import sys
from time import sleep

from drsmodule import constants
from drsmodule.locale import drs_text
from drsmodule.locale import drs_exceptions
from drsmodule.config.math import time


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_log.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get the parameter dictionary
ParamDict = constants.ParamDict
# Get the Config error
DrsError = drs_exceptions.DrsError
DrsWarning = drs_exceptions.DrsWarning
TextError = drs_exceptions.TextError
TextWarning = drs_exceptions.TextWarning
ConfigError = drs_exceptions.ConfigError
ConfigWarning = drs_exceptions.ConfigWarning
# Get the text types
ErrorEntry = drs_text.ErrorEntry
ErrorText = drs_text.ErrorText
HelpEntry = drs_text.HelpEntry
HelpText = drs_text.HelpText
# get the default language
DEFAULT_LANGUAGE = drs_text.DEFAULT_LANGUAGE
# Get the Color dict
Color = constants.Colors
# define log format
LOGFMT = Constants['DRS_LOG_FORMAT']


# =============================================================================
# Define classes
# =============================================================================
class Logger:
    def __init__(self, paramdict=None, instrument=None):
        """
        Construct logger (storage param dict here)
        :param paramdict:
        """
        func_name = __NAME__ + '.Logger.__init__()'
        # ---------------------------------------------------------------------
        # save the parameter dictionary for access to constants
        if paramdict is not None:
            self.pin = paramdict
            self.instrument = paramdict['INSTRUMENT']
            self.language = paramdict['LANGUAGE']
        elif instrument is not None:
            self.pin = constants.load(instrument)
            self.instrument = instrument
            self.language = paramdict['LANGUAGE']
        else:
            self.pin = constants.load()
            self.language = ['ENG']
            self.instrument = None
        # load additional resources based on instrument/language
        self.pconstant = constants.pload(self.instrument)
        self.errortext = ErrorText(self.instrument, self.language)
        self.helptext = HelpText(self.instrument, self.language)
        self.d_errortext = ErrorText(self.instrument, DEFAULT_LANGUAGE)
        self.d_helptext = HelpText(self.instrument, DEFAULT_LANGUAGE)
        # ---------------------------------------------------------------------
        # save output parameter dictionary for saving to file
        self.pout = ParamDict()

    def __call__(self, params=None, key='', message=None, printonly=False,
                 logonly=False, wrap=True, option=None, colour=None,
                 raise_exception=True):
        """
        Function-like cal to instance of logger (i.e. WLOG)
        Parses a key (error/warning/info/graph), an option and a message to the
        stdout and the log file.

        keys are controlled by "spirouConfig.Constants.LOG_TRIG_KEYS()"
        printing to screen is controlled by "PRINT_LEVEL" constant (config.py)
        printing to log file is controlled by "LOG_LEVEL" constant (config.py)
        based on the levels described in "spirouConfig.Constants.WRITE_LEVEL"

        :param params: parameter dictionary, ParamDict containing constants
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
        :param raise_exception: bool, If True exits if level is EXIT_LEVELS()

        output to stdout/log is as follows:

            HH:MM:SS.S - CODE |option|message

        time is output in UTC to nearest .1 seconds

        :return None:
        """
        func_name = __NAME__ + '.Logger.__call__()'
        # get character length
        char_len = self.pconstant.CHARACTER_LOG_LENGTH()
        # ---------------------------------------------------------------------
        # deal with message format (convert to ErrorEntry)
        if message is None:
            msg_obj = ErrorEntry('Unknown')
        elif type(message) is str:
            msg_obj = ErrorEntry(message)
        elif type(message) is list:
            msg_obj = ErrorEntry(message[0])
            for msg in message[1:]:
                msg_obj += ErrorEntry(msg)
        elif type(message) is ErrorEntry:
            msg_obj = message
        elif type(message) is HelpEntry:
            msg_obj = message.convert(ErrorEntry)
        else:
            msg_obj = ErrorEntry('00-005-00001', args=[message])
            key = 'error'
        # ---------------------------------------------------------------------
        # TODO: Remove deprecation warning (once all code changed)
        if type(params) is str:
            # Cannot add this to language pack - no p defined!
            emsg = ('Need to update WLOG function call. New format required:'
                    '\n\n\tNew format: WLOG(p, level_key, message)'
                    '\n\n\tOld format: WLOG(level_key, option, message)')
            raise DeprecationWarning(emsg)
        # ---------------------------------------------------------------------
        # deal with no p and pid
        if params is None:
            params = self.pin
            params['PID'] = None
            params.set_source('PID', func_name)
            # Cannot add this to language pack - no p defined!
            wmsg = 'Undefined PID not recommended (params is None)'
            DrsWarning(wmsg, level='warning')
        # deal with no PID
        if 'PID' not in params:
            params['PID'] = None
            # Cannot add this to language pack - no p defined!
            wmsg = 'Undefined PID not recommended (PID is missing)'
            DrsWarning(wmsg, level='warning')
        # deal with no instrument
        if 'INSTRUMENT' not in params:
            params['INSTRUMENT'] = None
        # deal with no language
        if 'LANGUAGE' not in params:
            params['LANGUAGE'] = 'ENG'
        # update pin and pconstant from p (selects instrument)
        self.update_param_dict(params)
        # ---------------------------------------------------------------------
        # deal with debug mode. If DRS_DEBUG is zero do not print these
        #     messages
        debug = params.get('DRS_DEBUG', 0)
        if key == 'debug' and debug == 0:
            return
        # ---------------------------------------------------------------------
        # deal with option
        if option is not None:
            option = option
        elif 'RECIPE' in params:
            option = params['RECIPE']
        else:
            option = ''
        # ---------------------------------------------------------------------
        # if key is '' then set it to all
        if len(key) == 0:
            key = 'all'
        # deal with both printonly and logonly set to True (bad)
        if printonly and logonly:
            printonly, logonly = False, False
        # check that key is valid
        if key not in self.pconstant.LOG_TRIG_KEYS():
            eargs = [key, 'LOG_TRIG_KEYS()']
            msg_obj += ErrorEntry('00-005-00002', args=eargs)
            key = 'error'
        if key not in self.pconstant.WRITE_LEVEL():
            eargs = [key, 'WRITE_LEVEL()']
            msg_obj += ErrorEntry('00-005-00003', args=eargs)
            key = 'error'
        if key not in self.pconstant.COLOUREDLEVELS():
            eargs = [key, 'COLOUREDLEVELS()']
            msg_obj += ErrorEntry('00-005-00004', args=eargs)
            key = 'error'
        if key not in self.pconstant.REPORT_KEYS():
            eargs = [key, 'REPORT_KEYS()']
            msg_obj += ErrorEntry('00-005-00005', args=eargs)
            key = 'error'
        # loop around message (now all are lists)
        errors = []
        # ---------------------------------------------------------------------
        # get log parameters (in set language)
        # ---------------------------------------------------------------------
        # Get the key code (default is a whitespace)
        code = self.pconstant.LOG_TRIG_KEYS().get(key, ' ')
        report = self.pconstant.REPORT_KEYS().get(key, False)
        # special case of report
        if debug >= 100:
            report = True
        # get messages
        if type(message) is HelpEntry:
            raw_message1 = msg_obj.get(self.helptext, report=report,
                                       reportlevel=key)
        else:
            raw_message1 = msg_obj.get(self.errortext, report=report,
                                       reportlevel=key)
        # split by '\n'
        raw_messages1 = raw_message1.split('\n')
        # ---------------------------------------------------------------------
        # deal with printing
        # ---------------------------------------------------------------------
        if not logonly:
            # loop around raw messages
            for mess in raw_messages1:
                # Get the time now in human readable format
                human_time = time.get_hhmmss_now()
                # storage for cmds
                cmds = []
                # check if line is over 80 chars
                if (len(mess) > char_len) and wrap:
                    # get new messages (wrapped at CHAR_LEN)
                    new_messages = textwrap(mess, char_len)
                    for new_message in new_messages:
                        cmdargs = [human_time, code, option, new_message]
                        cmd = LOGFMT.format(*cmdargs)
                        # append separate commands for log writing
                        cmds.append(cmd)
                        # add to logger storage
                        self.logger_storage(params, key, human_time, new_message,
                                            printonly)
                        # print to stdout
                        printlog(self, params, cmd, key, colour)
                else:
                    cmdargs = [human_time, code, option, mess]
                    cmd = LOGFMT.format(*cmdargs)
                    # append separate commands for log writing
                    cmds.append(cmd)
                    # add to logger storage
                    self.logger_storage(params, key, human_time, mess, printonly)
                    # print to stdout
                    printlog(self, params, cmd, key, colour)
        # ---------------------------------------------------------------------
        # get log parameters (in set language)
        # ---------------------------------------------------------------------
        # Get the key code (default is a whitespace)
        code = self.pconstant.LOG_TRIG_KEYS().get(key, ' ')
        report = self.pconstant.REPORT_KEYS().get(key, False)
        # get messages
        if type(message) is HelpEntry:
            raw_message2 = msg_obj.get(self.d_helptext, report=report,
                                       reportlevel=key)
        else:
            raw_message2 = msg_obj.get(self.d_errortext, report=report,
                                       reportlevel=key)
        # split by '\n'
        raw_messages2 = raw_message2.split('\n')
        # ---------------------------------------------------------------------
        # deal with logging (in default language)
        # ---------------------------------------------------------------------
        if not printonly:
            # loop around raw messages
            for mess in raw_messages2:
                # Get the time now in human readable format
                human_time = time.get_hhmmss_now()

                # clean up log message (no colour codes)
                mess = _clean_message(mess)

                # storage for cmds
                cmds = []
                cmdargs = [human_time, code, option, mess]
                cmd = LOGFMT.format(*cmdargs)
                # append separate commands for log writing
                cmds.append(cmd)
                # get logfilepath
                logfilepath, warning = get_logfilepath(self, params)
                # write to log file
                if len(warning) == 0:
                    for cmd in cmds:
                        writelog(self, params, cmd, key, logfilepath)
                # see if we have warning
                if warning and ('DRS_LOG_WARNING_ACTIVE' in params):
                    negate_warning = params['DRS_LOG_WARNING_ACTIVE']
                elif warning:
                    negate_warning = False
                    params['DRS_LOG_WARNING_ACTIVE'] = True
                    params.set_source('DRS_LOG_WARNING_ACTIVE', func_name)
                else:
                    negate_warning = True
                # if warning is True then we used TDATA and should report that
                if len(warning) > 0 and (not negate_warning):
                    if not logonly:
                        for warn in warning:
                            errors.append([warn, 'warning', human_time, option])

        # ---------------------------------------------------------------------
        # deal with errors caused by logging (print)
        # --------------------------------------------------------------------
        # print any errors caused above (and set key to error to exit after)
        used = []
        for error in errors:
            if error[1] == 'error':
                key = 'error'
            if error[0] not in used:
                self.logger_storage(params, key, error[2], error[0])
                printlogandcmd(self, params, *error, wrap=wrap, colour=colour)
                used.append(error[0])
        # ---------------------------------------------------------------------
        # deal with exiting
        # --------------------------------------------------------------------
        # deal with errors (if key is in EXIT_LEVELS) then exit after log/print
        if key in self.pconstant.EXIT_LEVELS():
            # prepare error string
            errorstring = ''
            for mess in raw_messages1:
                errorstring += mess + '\n'
            for error in errors:
                # must deal with lists of strings
                if type(error[0]) is list:
                    errorstring += ' \n'.join(error[0]) + '\n'
                # else we have a string
                else:
                    errorstring += error[0] + '\n'
            # deal with debugging
            if debug:
                debug_start(self, params, raise_exception)
            elif raise_exception:
                # self.pconstant.EXIT(p)(errorstring)
                self.pconstant.EXIT(params)()

    def update_param_dict(self, paramdict):
        # update the parameter dictionary
        for key in paramdict:
            # set pin value from paramdict
            self.pin[key] = paramdict[key]
            # set source from paramdict (or set to None)
            self.pin.set_source(key, paramdict.sources.get(key, None))
        # update these if "instrument" or "language" have changed
        cond1 = paramdict['INSTRUMENT'] != self.instrument
        cond2 = paramdict['LANGUAGE'] != self.language
        # only update if one of these has changed
        if cond1 or cond2:
            # update instrument
            self.instrument = paramdict['INSTRUMENT']
            # update language
            self.language = paramdict['LANGUAGE']
            # update pconstant
            self.pconstant = constants.pload(self.instrument)
            # updatetext
            self.errortext = ErrorText(self.instrument, self.language)
            self.helptext = HelpText(self.instrument, self.language)

    def output_param_dict(self, paramdict):
        func_name = __NAME__ + '.Logger.output_param_dict()'
        # get the process id from paramdict
        pid = paramdict['PID']
        # deal with no pid being set
        if pid not in self.pout:
            # get log storage keys
            storekey = self.pconstant.LOG_STORAGE_KEYS()
            for key in storekey:
                paramdict[key] = []
                # set the source
                paramdict.set_source(key, func_name)
            # return the parameter dictionary
            return paramdict
        # loop around the keys in pout
        for key in self.pout[pid]:
            # get value
            value = self.pout[pid][key]
            # set value from pout (make sure it is copied)
            paramdict[key] = type(value)(value)
            # set source from pout
            psource = self.pout[pid].sources.get(key, func_name)
            paramdict.set_source(key, psource)
        # return paramdict
        return paramdict

    def logger_storage(self, params, key, ttime, mess, printonly=False):
        func_name = __NAME__ + '.Logger.logger_storage()'
        if printonly:
            return 0
        # get pid
        pid =  params['PID']
        # make sub dictionary
        if pid not in self.pout:
            self.pout[pid] = ParamDict()
            self.pout.set_source(pid, func_name)
        # get log storage keys
        storekey = self.pconstant.LOG_STORAGE_KEYS()
        # find if key is defined in storage
        if key in storekey:
            # if key is in LOG just append message to list
            if storekey[key] in self.pout[pid]:
                self.pout[pid][storekey[key]].append([ttime, mess])
            # if key isn't in LOG make new list (for future append)
            else:
                self.pout[pid][storekey[key]] = [[ttime, mess]]
            # set the source
            self.pout[pid].set_source(storekey[key], func_name)
        # add to full log
        self.pout[pid]['LOGGER_FULL'].append([[ttime, mess]])

    def clean_log(self, processid):
        func_name = __NAME__ + '.Logger.clean_log()'
        # get log storage keys
        storekey = self.pconstant.LOG_STORAGE_KEYS()
        # clean out for this ID
        self.pout[processid] = ParamDict()
        self.pout.set_source(processid, func_name)
        # populate log keys
        for key in storekey:
            self.pout[processid][storekey[key]] = []
            # set the source
            self.pout[processid].set_source(storekey[key], func_name)
        # set the full logger key
        self.pout[processid]['LOGGER_FULL'] = []
        # set the source
        self.pout[processid].set_source('LOGGER_FULL', func_name)

class Printer():
    """Print things to stdout on one line dynamically"""
    def __init__(self, params, level, message):

        if type(message) not in [list, np.ndarray]:
            message = [message]
            sleeptimer = 0
        else:
            sleeptimer = 1

        for mess in message:
            sys.stdout.write("\r\x1b[K" + mess.__str__())
            sys.stdout.flush()
            sleep(sleeptimer)


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
        message = [logobj.errortext['00-005-00005'].format(message)]
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


def debug_start(logobj, p, raise_exception):
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
        def raw_input(x):
            return str(input(x))
    # get text
    text = logobj.errortext
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
        print(cc + text['00-005-00006'] + nocol)
        # noinspection PyUnboundLocalVariable
        uinput = raw_input(cc + text['00-005-00007'] + '\t' + nocol)
        if '1' in uinput.upper():
            print(cc + text['00-005-00008'] + nocol)

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
            # logobj.pconstant.EXIT(p)(errorstring)
            if raise_exception:
                logobj.pconstant.EXIT(p)()
        elif '2' in uinput.upper():
            print(cc + text['00-005-00009'] + nocol)

            import pdb
            pdb.set_trace()

            print(cc + text['00-005-00010'] + nocol)
            if raise_exception:
                logobj.pconstant.EXIT(p)()
        elif raise_exception:
            logobj.pconstant.EXIT(p)()
    except:
        if raise_exception:
            logobj.pconstant.EXIT(p)()


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
    errortext = ErrorText(p['INSTRUMENT'], p['LANGUAGE'])
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
            key = '10-005-00001'
            wmsg = errortext[key].format(*wargs)
            # if we have already display this warning don't again
            if wmsg in displayed_warnings:
                continue
            else:
                wlog(p, 'warning', ErrorEntry(key, args=wargs))
                displayed_warnings.append(wmsg)


def get_logfilepath(logobj, p):
    """
    Construct the log file path and filename (normally from "DRS_DATA_MSG"
    generates an ConfigError exception.

    "DRS_DATA_MSG" is defined in "config.py"

    :return lpath: string, the path and filename for the log file to be used
    :return warning: bool, if True print warnings about log file path
    """
    msgkey = 'DRS_DATA_MSG'
    # -------------------------------------------------------------------------
    # Get DRS_DATA_MSG folder directory
    dir_data_msg = p.get(msgkey, None)
    print_warnings = []
    # if None use "TDATA"
    if dir_data_msg is None:
        wmsg = logobj.errortext['10-005-00002'].format(msgkey)
        print_warnings += wmsg.split('\n')
        warning = True
    # if it doesn't exist also set to TDATA
    elif not os.path.exists(dir_data_msg):
        margs = [msgkey, p[msgkey]]
        wmsg = logobj.errortext['10-005-00003'].format(*margs)
        print_warnings += wmsg.split('\n')
        warning = True
    else:
        warning = False
    # do not save to log file
    if warning:
        return None, print_warnings
    else:
        lpath = logobj.pconstant.LOG_FILE_NAME(p, dir_data_msg)
        # return the logpath and the warning
        return lpath, print_warnings


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
        emsg = ErrorEntry('00-005-00011', args=[level, func_name])
        raise ConfigError(errorobj=[emsg, logobj.errortext])

    # get numeric value for this level
    try:
        thislevel = logobj.pconstant.WRITE_LEVEL()[key]
    except KeyError:
        emsg = ErrorEntry('00-005-00012', args=[key, func_name])
        raise ConfigError(errorobj=[emsg, logobj.errortext])

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
        emsg = ErrorEntry('00-005-00012', args=[level, func_name])
        raise ConfigError(errorobj=[emsg, logobj.errortext])

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
            eargs = [logfilepath, type(e), e, func_name]
            emsg = ErrorEntry('01-001-00011', args=eargs)
            raise ConfigError(errorobj=[emsg, logobj.errortext])
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
            eargs = [logfilepath, type(e), e, func_name]
            emsg = ErrorEntry('01-001-00011', args=eargs)
            raise ConfigError(errorobj=[emsg, logobj.errortext])


def _clean_message(message):

    # get all attributes of Color
    all_attr = Color.__dict__
    # storeage for codes
    codes = []
    # loop around and find codes
    for attr in all_attr:
        # get value for this attribute
        value = all_attr[attr]
        # find codes
        if type(value) is str:
            if value.__repr__().startswith('\'\\x'):
                codes.append(value)

    # find codes in message
    for code in codes:
        if code in message:
            message = str(message.replace(code, ''))
    # return message
    return message


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

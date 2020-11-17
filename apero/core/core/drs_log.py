#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
spirouCore.py

Logging related functions

Created on 2017-10-11 at 10:59

@author: cook

Import rules:
    only from core.math, core.constants, apero.lang, apero.base

    do not import from core.core.drs_argument
    do not import from core.core.drs_file

Version 0.0.1
"""
from astropy.table import Table
from collections import OrderedDict
import numpy as np
import os
from pathlib import Path
import sys
from time import sleep
from typing import Any, List, Tuple, Union

from apero.base import base
from apero.core.core import drs_exceptions
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero.core import constants
from apero import lang
from apero.core.math import time

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_log.py'
__INSTRUMENT__ = 'None'
# Get version and author
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get the parameter dictionary
ParamDict = constants.ParamDict
# Get the Config error
DrsCodedException = drs_exceptions.DrsCodedException
DrsCodedWarning = drs_exceptions.DrsCodedWarning
# Get the text types
textentry = lang.textentry
# get the default language
DEFAULT_LANGUAGE = lang.core.drs_lang_text.DEFAULT_LANGUAGE
# Get the Color dict
Color = drs_misc.Colors()


# =============================================================================
# Define classes
# =============================================================================
class Logger:
    def __init__(self, paramdict: ParamDict = None, instrument: str = None):
        """
        Construct logger class - for all the printing to screen and to log file
        Normally used via the call and this class is only constructed once.

        :param paramdict:
        """
        # set class name
        self.class_name = 'Logger'
        # set function name
        _ = drs_misc.display_func(None, '__init__', __NAME__, self.class_name)
        # ---------------------------------------------------------------------
        # save the parameter dictionary for access to constants
        if paramdict is not None:
            self.pin = paramdict
            self.instrument = paramdict.get('INSTRUMENT', None)
            self.language = paramdict.get('LANGUAGE', 'ENG')
        elif instrument is not None:
            self.pin = constants.load(instrument)
            self.instrument = instrument
            self.language = paramdict['LANGUAGE']
        else:
            self.pin = constants.load()
            self.language = 'ENG'
            self.instrument = 'None'
        # load additional resources based on instrument/language
        self.pconstant = constants.pload(self.instrument)
        # ---------------------------------------------------------------------
        # save output parameter dictionary for saving to file
        self.pout = ParamDict()
        # get log storage keys
        storekey = self.pconstant.LOG_STORAGE_KEYS()
        # add log stats to pout
        for key in storekey:
            self.pout[storekey[key]] = []
        self.pout['LOGGER_FULL'] = []

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = ['pconstant', 'textdict', 'helptext', 'd_textdict',
                   'd_helptext']
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__:
            if key not in exclude:
                state[key] = item
        # return dictionary state
        return state

    def __setstate__(self, state):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)
        # read attributes not in state
        self.pconstant = constants.pload(self.instrument)

    def __str__(self) -> str:
        """
        String representation of the logger
        :return:
        """
        return 'Logger[{0}][{1}]'.format(self.instrument, self.language)

    def __repr__(self) -> str:
        """
        String representation of the logger
        :return:
        """
        return self.__str__()

    def __call__(self, params: ParamDict = None, key: str = '',
                 message: Union[str, None] = None,
                 printonly: bool = False,
                 logonly: bool = False, wrap: bool = True,
                 option: str = None, colour: str = None,
                 raise_exception: bool = True):
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
                       p['RECIPE'] or DRS_USER_PROGRAM
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
        # set function name
        func_name = drs_misc.display_func(None, '__call__', __NAME__,
                                          self.class_name)
        # ---------------------------------------------------------------------
        # deal with debug mode. If DRS_DEBUG is zero do not print these
        #     messages
        if params is not None:
            debug = params.get('DRS_DEBUG', 0)
            if key == 'debug' and debug < params['DEBUG_MODE_LOG_PRINT']:
                return
        else:
            debug = 0
        # if in debug mode don't wrap
        if debug > 0 and (key == 'debug'):
            wrap = False
        # ---------------------------------------------------------------------
        # get character length
        char_len = self.pconstant.CHARACTER_LOG_LENGTH()
        # ---------------------------------------------------------------------
        # deal with message format (convert to lang.Text)
        if message is None:
            msg_obj = textentry('Unknown')
        elif type(message) is str:
            msg_obj = textentry(message)
        elif type(message) is list:
            msg_obj = textentry(message[0])
            for msg in message[1:]:
                msg_obj += textentry(msg)
        else:
            msg_obj = textentry('00-005-00001', args=[message])
            key = 'error'
        # ---------------------------------------------------------------------
        # deal with no p and pid
        if params is None:
            params = self.pin
            params['PID'] = None
            params.set_source('PID', func_name)
            # Cannot add this to language pack - no p defined!
            DrsCodedWarning('10-005-00005', 'warning', func_name=func_name)
        # deal with no PID
        if 'PID' not in params:
            params['PID'] = None
            # Cannot add this to language pack - no p defined!
            DrsCodedWarning('10-005-00006', 'warning', func_name=func_name)
        # deal with no instrument
        if 'INSTRUMENT' not in params:
            params['INSTRUMENT'] = base.IPARAMS['INSTRUMENT']
        # deal with no language
        if 'LANGUAGE' not in params:
            params['LANGUAGE'] = base.IPARAMS['LANGUAGE']
        # update pin and pconstant from p (selects instrument)
        self.update_param_dict(params)
        # ---------------------------------------------------------------------
        # deal with option
        if option is not None:
            option = option
        elif 'RECIPE' in params:
            option = str(params.get('RECIPE', ''))
        else:
            option = ''
        # overwrite these with DRS_USER_PROGRAM (if not None)
        userprogram = str(params.get('DRS_USER_PROGRAM', None))
        if userprogram != 'None':
            option = userprogram

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
            msg_obj += textentry('00-005-00002', args=eargs)
            key = 'error'
        if key not in self.pconstant.WRITE_LEVEL():
            eargs = [key, 'WRITE_LEVEL()']
            msg_obj += textentry('00-005-00003', args=eargs)
            key = 'error'
        if key not in self.pconstant.COLOUREDLEVELS():
            eargs = [key, 'COLOUREDLEVELS()']
            msg_obj += textentry('00-005-00004', args=eargs)
            key = 'error'
        if key not in self.pconstant.REPORT_KEYS():
            eargs = [key, 'REPORT_KEYS()']
            msg_obj += textentry('00-005-00005', args=eargs)
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
        if debug >= params['DEBUG_MODE_TEXTNAME_PRINT']:
            report = True
        # get messages
        if isinstance(msg_obj, lang.Text):
            raw_messages1 = msg_obj.get_text(report=report, reportlevel=key)
        else:
            raw_messages1 = str(msg_obj)
        # split by '\n'
        raw_messages1 = raw_messages1.split('\n')
        # ---------------------------------------------------------------------
        # deal with printing
        # ---------------------------------------------------------------------
        if not logonly:
            # loop around raw messages
            for mess in raw_messages1:
                # add a space to the start of messages (if not present)
                if not mess.startswith(' '):
                    mess = ' ' + mess
                # Get the time now in human readable format
                human_time = time.get_hhmmss_now()
                # storage for cmds
                cmds = []
                # check if line is over 80 chars
                if (len(mess) > char_len) and wrap:
                    # get new messages (wrapped at CHAR_LEN)
                    new_messages = drs_text.textwrap(mess, char_len)
                    for new_message in new_messages:
                        # add a space to the start of messages (if not present)
                        if not new_message.startswith(' '):
                            new_message = ' ' + new_message
                        cmdargs = [human_time, code, option, new_message]
                        cmd = params['DRS_LOG_FORMAT'].format(*cmdargs)
                        # append separate commands for log writing
                        cmds.append(cmd)
                        # add to logger storage
                        self.logger_storage(params, key, human_time,
                                            new_message, printonly)
                        # print to stdout
                        printlog(self, params, cmd, key, colour)
                else:
                    cmdargs = [human_time, code, option, mess]
                    cmd = params['DRS_LOG_FORMAT'].format(*cmdargs)
                    # append separate commands for log writing
                    cmds.append(cmd)
                    # add to logger storage
                    self.logger_storage(params, key, human_time, mess,
                                        printonly)
                    # print to stdout
                    printlog(self, params, cmd, key, colour)
        # ---------------------------------------------------------------------
        # get log parameters (in set language)
        # ---------------------------------------------------------------------
        # Get the key code (default is a whitespace)
        code = self.pconstant.LOG_TRIG_KEYS().get(key, ' ')
        # report = self.pconstant.REPORT_KEYS().get(key, False)
        # get messages
        if isinstance(msg_obj, lang.Text):
            raw_messages2 = msg_obj.get_text(report=True, reportlevel=key)
        else:
            raw_messages2 = str(msg_obj)
        # split by '\n'
        raw_messages2 = raw_messages2.split('\n')
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
                cmd = params['DRS_LOG_FORMAT'].format(*cmdargs)
                # append separate commands for log writing
                cmds.append(cmd)
                # get logfilepath
                logfilepath = get_logfilepath(self, params)
                # write to log file
                writelog(self, params, cmd, key, logfilepath)

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
                raise drs_exceptions.LogExit(errorstring)

    def update_param_dict(self, paramdict: ParamDict):
        """
        Update the parameter dictionary when a change in instrument or
        language is detected

        :param paramdict: ParamDict, the parameter dictionary of constants to
                          update
        :return:
        """
        # set function name
        _ = drs_misc.display_func(paramdict, 'update_param_dict', __NAME__,
                                  self.class_name)
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

    def output_param_dict(self, paramdict: ParamDict,
                          new: bool = False) -> ParamDict:
        """
        Push the LOG_STORAGE_KEYS into a parameter dictionary (either new
        if new = True or self.pout otherwise and return it

        :param paramdict: ParamDict, the current constants parameter dictionary
        :param new: bool, if True populate and return a new ParamDict instead
                    of updating self.pout
        :return:
        """
        # set function name
        func_name = drs_misc.display_func(paramdict, 'output_param_dict',
                                          __NAME__, self.class_name)
        # get the process id from paramdict
        pid = paramdict['PID']
        # deal with new switch
        if new:
            pdict = ParamDict()
        else:
            pdict = paramdict
        # deal with no pid being set
        if pid not in self.pout:
            # get log storage keys
            storekey = self.pconstant.LOG_STORAGE_KEYS()
            for key in storekey:
                pdict[key] = []
                # set the source
                pdict.set_source(key, func_name)
            # return the parameter dictionary
            return pdict
        # loop around the keys in pout
        for key in self.pout[pid]:
            # get value
            value = self.pout[pid][key]
            # set value from pout (make sure it is copied)
            pdict[key] = type(value)(value)
            # set source from pout
            psource = self.pout[pid].sources.get(key, func_name)
            pdict.set_source(key, psource)
        # return paramdict
        return pdict

    def logger_storage(self, params: ParamDict, key: str,
                       ttime: str, mess: str, printonly: bool = False):
        """
        Stoger log messages in a dictionary (for access later)
        stored in Logger.pout

        :param params: ParamDict, the constants parameter dictionary
        :param key: str, the key to append (normally the log level)
        :param ttime: str, the human time HH:MM:SS.SS
        :param mess: str, the log message to store
        :param printonly: bool, if True do not log (we are only printing the
                          message not logging it)
        :return: None
        """
        # set function name
        func_name = drs_misc.display_func(params, 'logger_storage',
                                          __NAME__, self.class_name)
        # if we are printing only just return
        if printonly:
            return 0
        # get pid
        pid = params['PID']
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
        if 'LOGGER_FULL' in self.pout[pid]:
            self.pout[pid]['LOGGER_FULL'].append([[ttime, mess]])
        else:
            self.pout[pid]['LOGGER_FULL'] = [[ttime, mess]]

    def clean_log(self, processid: str):
        """
        Clean the log of all entries for a specific process id

        :param processid: str, the unique apero process ID generated once
                          per recipe run
        :return:
        """
        # set function name
        func_name = drs_misc.display_func(self.pin, 'clean_log',
                                          __NAME__, self.class_name)
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

    def printmessage(self, params: ParamDict, messages: Union[str, List[str]],
                     colour: Union[str, None] = None):
        """
        Print the log message(s) in a certain colour (not at a certain level)

        :param params: ParamDict, the parameter dictionary of constants,
                       required to get levels to print at etc
        :param messages: list of strings or string, the message(s) to print
        :param colour: string, the colour wanted for the printed message
        :return: None
        """
        # check whether message is string (if so make a list)
        if isinstance(messages, str):
            messages = [messages]
        # loop around messages
        for message in messages:
            printlog(self, params, message, key='all', colour=colour)

    def logmessage(self, params: ParamDict, messages: Union[str, List[str]]):
        """
        Writes the log message(s) to disk

        :param params: ParamDict, the parameter dictionary of constants,
                       required to get levels to print at etc
        :param messages: list of strings or string, the message(s) to print

        :return: None
        """
        # get logfilepath
        logfilepath = get_logfilepath(self, params)
        # check whether message is string (if so make a list)
        if isinstance(messages, str):
            messages = [messages]
        # loop around messages
        for message in messages:
            writelog(self, params, message, key='all', logfilepath=logfilepath)


class Printer:
    """Print things to stdout on one line dynamically"""

    def __init__(self, params: Union[ParamDict, None], level: Union[str, None],
                 message: Union[list, np.ndarray, str]):
        """
        Dynamically print text to stdout, flushing the line so it appears
        to come from only one line (does not have new lines)

        :param params: ParamDict, the constants parameter dictionary
                       (Not used but here to emulate Logger.__call__())
        :param level: str,
        :param message:
        """
        # set class name
        self.class_name = 'Printer'
        # set function name
        _ = drs_misc.display_func(None, '__init__', __NAME__, self.class_name)
        # set params and level
        self.params = params
        self.level = level

        if type(message) not in [list, np.ndarray]:
            message = [message]
            sleeptimer = 0
        else:
            sleeptimer = 1

        for mess in message:
            sys.stdout.write("\r\x1b[K" + mess.__str__())
            sys.stdout.flush()
            sleep(sleeptimer)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)


class RecipeLog:

    def __init__(self, name: str, params: ParamDict, level: int = 0,
                 logger: Union[None, Logger] = None):
        """
        Constructor for the recipe log

        :param name: str, the recipe name this recipe log belong to
        :param params: ParamDict, the constants parameter dictionary
        :param level: int, the level of this log 0 is root, higher numbers are
                      children of the root
        :param logger: if set the WLOG (Logger) instance to use
        """
        # set class name
        self.class_name = 'RecipeLog'
        # set function name
        _ = drs_misc.display_func(None, '__init__', __NAME__, self.class_name)
        # get the recipe name
        self.name = str(name)
        # the kind of recipe ("recipe", "tool", "processing") from recipe.kind
        self.kind = str(params['DRS_RECIPE_KIND'])
        # the default logging absolute path
        self.defaultpath = str(params['DRS_DATA_MSG_FULL'])
        # the log fits file name (log.fits)
        self.logfitsfile = str(params['DRS_LOG_FITS_NAME'])
        # the recipe input directory from recipe.inputdir
        self.inputdir = str(params['INPATH'])
        # the recipe output directory from recipe.outputdir
        self.outputdir = str(params['OUTPATH'])
        # the parameter dictionary of constants
        self.params = params
        # the Logger instances (or None)
        self.wlog = logger
        # set the pid
        self.pid = str(params['PID'])
        # set the human time
        self.htime = str(params['DATE_NOW'])
        # set the group name
        self.group = str(params['DRS_GROUP'])
        # set the night name directory (and deal with no value)
        if 'NIGHTNAME' not in params:
            self.directory = 'other'
        elif params['NIGHTNAME'] in [None, 'None', '']:
            self.directory = 'other'
        else:
            self.directory = str(params['NIGHTNAME'])
        # get log fits path
        self.logfitspath = self._get_write_dir()
        # define lockfile (we need to lock the directory while this is
        #   being done)
        self.lockfile = self.directory + self.logfitsfile.replace('.', '_')
        # set the log file name (just used to save log directory)
        #  for log table entry
        self.log_file = 'None'
        # set the plot file name (just used to save the plot directory) for
        #   log table entry
        self.plot_dir = 'None'
        # set the inputs
        self.args = ''
        self.kwargs = ''
        self.skwargs = ''
        self.runstring = ''
        # set that recipe started
        self.started = True
        # set the iteration
        self.set = []
        # set the level (top level=0)
        self.level = level
        # set the level criteria
        self.level_criteria = ''
        self.level_iteration = 0
        # set qc
        self.passed_qc = False
        # set qc paarams
        self.qc_string = ''
        self.qc_name = ''
        self.qc_value = ''
        self.qc_pass = ''
        self.qc_logic = ''
        # set the errors
        self.errors = ''
        # set that recipe ended
        self.ended = False
        # set lock function
        self.lfunc = None

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        String representation of this class
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, '__str__', __NAME__, self.class_name)
        # return string representation of RecipeLOg
        return 'RecipeLog[{0}]'.format(self.name)

    def copy(self, rlog: 'RecipeLog'):
        """
        Copy another RecipeLog over this one

        :param rlog: Another RecipeLog instance
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'copy', __NAME__, self.class_name)
        # copy parameters
        self.name = str(rlog.name)
        self.kind = str(rlog.kind)
        self.defaultpath = str(rlog.defaultpath)
        self.inputdir = str(rlog.inputdir)
        self.outputdir = str(rlog.outputdir)
        self.pid = str(rlog.pid)
        self.htime = str(rlog.htime)
        self.group = str(rlog.group)
        self.directory = str(rlog.directory)
        self.logfitspath = str(rlog.logfitspath)
        self.lockfile = str(rlog.lockfile)
        self.log_file = str(rlog.log_file)
        self.runstring = str(rlog.runstring)
        self.args = str(rlog.args)
        self.kwargs = str(rlog.kwargs)
        self.skwargs = str(rlog.skwargs)
        self.level_criteria = str(rlog.level_criteria)
        self.lfunc = rlog.lfunc

    def set_log_file(self, logfile: Union[str, Path]):
        """
        Set the log file

        :param logfile: str, the log file
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'set_log_file', __NAME__,
                                  self.class_name)
        # set the log file
        self.log_file = str(logfile)

    def set_plot_dir(self, params: ParamDict,
                     location: Union[str, Path, None] = None,
                     write: bool = True):
        """
        Set the plot directory for RecipeLog and all children

        :param params: ParamDict, the constants parameter dictionary
        :param location: str or Path, the path of the plot directory
        :param write: bool, if True update the log file
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'set_plot_dir', __NAME__,
                                  self.class_name)
        # deal with location being set
        if location is not None:
            self.plot_dir = str(location)
            # update children
            if len(self.set) != 0:
                for child in self.set:
                    child.set_plot_dir(params, location, write=False)
        else:
            self.plot_dir = 'None'
        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def set_lock_func(self, func: Any):
        """
        Set the lock function apero.io.drs_lock.locker

        :param func: the locking function apero.io.drs_lock.locker
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'set_lock_func', __NAME__,
                                  self.class_name)
        # set the lock function
        self.lfunc = func

    def add_level(self, params: ParamDict, key: str, value: Any,
                  write: bool = True) -> 'RecipeLog':
        """
        Add a child level to the recipe log i.e. inside a for loop we may want
        one log entry for each iteration (level is incremented - root = 0)

        :param params: ParamDict, the constants parameter dictionary
        :param key: str, text describing this new level (i.e. fiber or
                    iteration) converted to key = value
                    e.g.  key: fiber
                              we have a level with the following:
                              fiber = A
                              fiber = B
                              fiber = C

        :param value: Any (must be convertable to string) the value of this
                      iterations key  i.e. key = value
        :param write: bool, if True writes to RecipeLog fits file
        :return: RecipeLog, the child instance of the parent RecipeLog
                 all children are stored inside a parent
        """
        # set function name
        _ = drs_misc.display_func(None, 'add_level', __NAME__, self.class_name)
        # get new level
        level = self.level + 1
        # create new log
        newlog = RecipeLog(self.name, params, level=level, logger=self.wlog)
        # copy from parent
        newlog.copy(self)
        # record level criteria
        newlog.level_criteria += '{0}={1} '.format(key, value)
        # update the level iteration
        newlog.level_iteration = len(self.set)
        # add newlog to set
        self.set.append(newlog)
        # whether to write (update) recipe log file
        if write:
            newlog.write_logfile(params)
        # return newlog (for use)
        return newlog

    def add_qc(self, params: ParamDict,
               qc_params: Tuple[List[str], List[Any], List[str], List[int]],
               passed: Union[int, bool, str], write: bool = True):
        """
        Add the quality control criteria (stored in qc_params) to the recipe
        log

        :param params: Paramdict, the constants parameter dictionary
        :param qc_params: the quality control storage, constists of
                          qc_names, qc_values, qc_logic, qc_pass where
                          qc_names is a list of variable names,
                          qc_values is a list of value for each variable
                          qc_logic is the pass/fail logic for variable
                          qc_pass is either 1 for passed qc or 0 for failure
        :param passed: int/bool/str if 1 or True or '1' all quality control was
                       passed (this is stored as a column in log database)
        :param write: bool, if True write parameters to log database
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'add_qc', __NAME__, self.class_name)
        # update passed
        if passed in [1, True, '1']:
            self.passed_qc = True
        else:
            self.passed_qc = False
        # update qc params
        qc_names, qc_values, qc_logic, qc_pass = qc_params
        for it in range(len(qc_names)):
            # deal with no qc set
            if qc_names[it] in ['None', None, '']:
                continue

            # set up qc pass string
            if qc_pass[it]:
                pass_str = 'PASSED'
            else:
                pass_str = 'FAILED'
            # deal with qc set
            qargs = [qc_names[it], qc_values[it], qc_logic[it], pass_str]
            self.qc_string += '{0}={1} [{2}] {3} ||'.format(*qargs)
            self.qc_name += '{0}||'.format(qc_names[it])
            self.qc_value += '{0}||'.format(qc_values[it])
            self.qc_logic += '{0}||'.format(qc_logic[it])
            self.qc_pass += '{0}||'.format(qc_pass[it])

        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def no_qc(self, params: ParamDict, write: bool = True):
        """
        Writes that quality control passed (there were no quality control)

        :param params: ParamDict, the constants parameter dictionary
        :param write: bool, whether to write to log database
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'no_qc', __NAME__, self.class_name)
        # set passed_qc to True (no qc means automatic pass)
        self.passed_qc = True
        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def add_error(self, params: ParamDict, errortype: Union[Exception, str],
                  errormsg: str, write: bool = True):
        """
        Add an error (exception) to the database in the errors column
        errors are separate by two ||

            ErrorType: ErrorMessage ||

        :param params: ParamDict, the constants parameter dictionary
        :param errortype: Exception or string, the error exception or a string
                          representation of it
        :param errormsg: str, the error message to store
        :param write: bool, if True writes to the log database
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'add_error', __NAME__, self.class_name)
        # add errors in form ErrorType: ErrorMessage ||
        self.errors += '"{0}":"{1}"||'.format(errortype, errormsg)
        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def end(self, params: ParamDict, write: bool = True):
        """
        Add the row that says recipe finished correctly to database

        :param params: ParamDict, the constants parameter dictionary
        :param write: bool, whether to write to log database
        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'end', __NAME__, self.class_name)
        # set the ended parameter to True
        self.ended = True
        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def write_logfile(self, params: ParamDict):
        """
        The lcoked writer function - do not use _writer directly
        this locks the write procses using the predefined lock function

        :param params: ParamDict, the constants parameter dictionary

        :return: None
        """
        # set function name
        _ = drs_misc.display_func(None, 'end', __NAME__, self.class_name)
        # do not write the lock file is a lock file is not present
        if self.lfunc is None:
            return
        # if we do have a lock file then we can write using a lock file and
        #   the _writer function
        else:
            self.lfunc(params, self.lockfile, self._writer)

    # private methods
    def _get_write_dir(self) -> str:
        """
        Construct the recipe log write directory from RecipeLog.outputdir
        and RecipeLog.directory and RecipeLog.logfitsfile

        :return: str, the write path for the RecipeLog file
        :raises: drs_exceptions.LogExit if path is not valid
        """
        # set function name
        _ = drs_misc.display_func(None, '_get_write_dir', __NAME__,
                                  self.class_name)
        # ------------------------------------------------------------------
        # get log path
        if self.outputdir not in ['None', '', None]:
            path = os.path.join(self.outputdir, self.directory)
        # else use the default path
        else:
            path = self.defaultpath
        # ------------------------------------------------------------------
        # check that directory exists
        if not os.path.exists(path):
            # noinspection PyBroadException
            try:
                os.makedirs(path)
            except Exception as _:
                # RecipeLogError: Cannot make path {0} for recipe log.'
                eargs = [path]
                emsg = textentry('00-005-00014', args=eargs)
                if self.wlog is not None:
                    self.wlog(self.params, 'error', emsg)
        # ------------------------------------------------------------------
        # return absolute log file path
        return os.path.join(path, self.logfitsfile)

    def _make_row(self) -> OrderedDict:
        """
        Make a row in the RecipeLog file
        :return: OrderedDict the row entry where each key is a column name
        """
        # set function name
        _ = drs_misc.display_func(None, '_make_row', __NAME__, self.class_name)
        # set rows
        row = OrderedDict()
        row['RECIPE'] = self.name
        row['KIND'] = self.kind
        row['PID'] = self.pid
        row['HTIME'] = self.htime
        row['GROUP'] = self.group
        row['LEVEL'] = self.level
        row['SUBLEVEL'] = self.level_iteration
        row['LEVEL_CRIT'] = self.level_criteria
        row['INPATH'] = self.inputdir
        row['OUTPATH'] = self.outputdir
        row['DIRECTORY'] = self.directory
        row['LOGFILE'] = self.log_file
        row['PLOTDIR'] = self.plot_dir
        row['RUNSTRING'] = self.runstring
        # add inputs
        row['ARGS'] = self.args
        row['KWARGS'] = self.kwargs
        row['SKWARGS'] = self.skwargs
        # add whether recipe started
        row['STARTED'] = self.started
        # add whether all qc passed
        row['PASSED_ALL_QC'] = self.passed_qc
        # qc columns
        row['QC_STRING'] = self.qc_string.strip().strip('||').strip()
        row['QC_NAMES'] = self.qc_name.strip().strip('||').strip()
        row['QC_VALUES'] = self.qc_value.strip().strip('||').strip()
        row['QC_LOGIC'] = self.qc_logic.strip().strip('||').strip()
        row['QC_PASS'] = self.qc_pass.strip().strip('||').strip()
        # add errors
        row['ERRORS'] = self.errors
        # add whether recipe ended
        row['ENDED'] = self.ended
        # return row
        return row

    def get_rows(self) -> List[OrderedDict]:
        """
        Get all rows for a entry (including all rows from the child Recipelog
        entries

        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, '_get_rows', __NAME__, self.class_name)
        # set rows storage
        rows = []
        # case where we have no sets
        if len(self.set) == 0:
            rows.append(self._make_row())
        else:
            # else we have children
            for child in self.set:
                rows += child.get_rows()
        # return rows
        return rows

    def _writer(self):
        """
        The actual write function for the RecipeLog

        :return:
        """
        # set function name
        func_name = drs_misc.display_func(None, '_writer', __NAME__,
                                          self.class_name)
        # get write path
        writepath = self.logfitspath
        # ------------------------------------------------------------------
        # check to see if table already exists
        if os.path.exists(writepath):
            try:
                # RecipeLog: Reading file
                dargs = [writepath]
                dmsg = textentry('90-008-00012', args=dargs)
                if self.wlog is not None:
                    self.wlog(self.params, 'debug', dmsg)
                table = Table.read(writepath, format='fits')
            except Exception as e:
                # RecipeLogError: Cannot read file
                eargs = [writepath, type(e), str(e)]
                emsg = textentry('00-005-00016', args=eargs)
                if self.wlog is not None:
                    self.wlog(self.params, 'error', emsg)
                    return
                else:
                    raise DrsCodedException('00-005-00016', level='error',
                                            targs=eargs, func_name=func_name)
        else:
            table = None
        # ------------------------------------------------------------------
        # if pid in table remove all lines containing it (start with a clean
        #   table)
        if table is not None:
            # find all rows with same PID
            mask = self.pid == table['PID']
            # find all rows with same level iteration
            mask &= self.level_iteration == table['SUBLEVEL']
            # keep all files that don't match mask
            if np.sum(mask) > 0:
                table = table[~mask]
        # ------------------------------------------------------------------
        # generate row(s) to add to table
        rows = self.get_rows()
        # ------------------------------------------------------------------
        # add rows to table
        # ------------------------------------------------------------------
        tabledict = OrderedDict()
        # ------------------------------------------------------------------
        # populate with old table
        if table is not None:
            for col in table.colnames:
                # deal with having
                tabledict[col] = list(table[col])
        # ------------------------------------------------------------------
        # loop around rows and add to tabledict
        for row in rows:
            # loop around columns in row
            for col in row:
                # get column value
                cvalue = row[col]
                # deal with '' and None
                if cvalue in ['', 'None', None]:
                    cvalue = 'None'
                # append to table
                if col in tabledict:
                    tabledict[col].append(cvalue)
                # deal with column not in table dict (should only happen when
                #   we have no previous rows/no previous table)
                else:
                    tabledict[col] = [cvalue]
        # ------------------------------------------------------------------
        # create new master table
        mastertable = Table()
        for col in tabledict:
            mastertable[col] = tabledict[col]
        # ------------------------------------------------------------------
        # write to disk
        try:
            # debug log
            if self.wlog is not None:
                dargs = [writepath]
                dmsg = textentry('90-008-00011', args=dargs)
                self.wlog(self.params, 'debug', dmsg)
            mastertable.write(writepath, format='fits', overwrite=True)
        except Exception as e:
            # RecipeLogError: Cannot write file {0}
            if self.wlog is not None:
                eargs = [writepath, type(e), str(e)]
                emsg = textentry('00-005-00015', args=eargs)
                self.wlog(self.params, 'error', emsg)


# =============================================================================
# Define our instance of wlog
# =============================================================================
# Get our instance of logger
wlog = Logger()


# =============================================================================
# Define Logger functions
# =============================================================================
def printlogandcmd(logobj: Logger, params: ParamDict,
                   message: Union[str, List[str]], key: str,
                   human_time: str, option: str, wrap: bool = True,
                   colour: str = 'green'):
    """
    Prints log to standard output/screen (for internal use only when
    logger cannot be used)

        output to stdout is as follows:

        HH:MM:SS.S - CODE |option|message

    :param logobj: logger instance, the logger object (for pconstant)
    :param params: ParamDict, the constants file passed from call
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
        message = [textentry('00-005-00005', args=message)]
        key = 'error'
    for mess in message:
        code = logobj.pconstant.LOG_TRIG_KEYS().get(key, ' ')
        # check if line is over 80 chars
        if (len(mess) > char_len) and wrap:
            # get new messages (wrapped at CHAR_LEN)
            new_messages = drs_text.textwrap(mess, char_len)
            for new_message in new_messages:
                cmdargs = [human_time, code, option, new_message]
                cmd = params['DRS_LOG_FORMAT'].format(*cmdargs)
                printlog(logobj, params, cmd, key, colour)
        else:
            cmdargs = [human_time, code, option, mess]
            cmd = params['DRS_LOG_FORMAT'].format(*cmdargs)
            printlog(logobj, params, cmd, key, colour)


def debug_start(logobj: Logger, params: ParamDict,
                raise_exception: bool = True):
    """
    Initiate debugger (for DEBUG mode) - will start when an error is raised
    if 'DRS_DEBUG' is set to True or 1 (in config.py)

    :param logobj: logger instance, the logger object (for pconstant)
    :param params: the ParamDict of constants
    :param raise_exception: bool, if True raises an exception on error

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
    # get colour
    clevels = logobj.pconstant.COLOUREDLEVELS()
    addcolour = params.get('DRS_COLOURED_LOG', True)

    nocol = Color.ENDC
    if addcolour:
        cc = clevels['error']
    else:
        cc = nocol
    # ask to run debugger
    # noinspection PyBroadException
    try:
        print(cc + textentry('00-005-00006') + nocol)
        # noinspection PyUnboundLocalVariable
        uinput = raw_input(cc + textentry('00-005-00007') + '\t' + nocol)
        if '1' in uinput.upper():
            print(cc + textentry('00-005-00008') + nocol)

            # noinspection PyBroadException
            try:
                from IPython import embed
                # noinspection PyUnboundLocalVariable
                ipython = embed
                import ipdb
                ipdb.set_trace()
            except Exception as _:
                import pdb
                pdb.set_trace()

            print(cc + '\n\nCode Exited' + nocol)
            # logobj.pconstant.EXIT(p)(errorstring)
            if raise_exception:
                logobj.pconstant.EXIT(params)()
        elif '2' in uinput.upper():
            print(cc + textentry('00-005-00009') + nocol)

            import pdb
            pdb.set_trace()

            print(cc + textentry('00-005-00010') + nocol)
            if raise_exception:
                logobj.pconstant.EXIT(params)()
        elif raise_exception:
            logobj.pconstant.EXIT(params)()
    except Exception as _:
        if raise_exception:
            logobj.pconstant.EXIT(params)()


def display_func(params: Union[ParamDict, None] = None,
                 name: Union[str, None] = None,
                 program: Union[str, None] = None,
                 class_name: Union[str, None] = None) -> str:
    """
    Alias to display function (but always with wlog set from Logger()

    :param params: None or ParamDict (containing "INPUTS" for breakfunc/
                   breakpoint)
    :param name: str or None - if set is the name of the function
                 (i.e. def myfunction   name = "myfunction")
                 if unset, set to "Unknown"
    :param program: str or None, the program or recipe the function is defined
                    in, if unset not added to the output string
    :param class_name: str or None, the class name, if unset not added
                       (i.e. class myclass   class_name = "myclass"

    :return: a properly constructed string representation of where the
              function is.
    """
    # set function name (obviously can't use display func here)
    func_name = __NAME__ + 'display_func()'
    # check display_func (must be ParamDict or None)
    if params is not None and not isinstance(params, ParamDict):
        # log error
        eargs = [type(params), str(params)[:20], func_name]
        raise DrsCodedException('00-001-00050', targs=eargs, level='error',
                                func_name=func_name)
    # run the display function
    return drs_misc.display_func(params, name, program, class_name, wlog=wlog)


def warninglogger(params: ParamDict, warnlist: Any,
                  funcname: Union[str, None] = None):
    """
    Warning logger - takes "w" - a list of caught warnings and pipes them on
    to the log functions. If "funcname" is not None then t "funcname" is
    printed with the line reference (intended to be used to identify the code/
    function/module warning was generated in)

    to catch warnings use the following:

    >> import warnings
    >> with warnings.catch_warnings(record=True) as warnlist:
    >>     code_to_generate_warnings()
    >> warninglogger(parmas, warnlist, 'some function name for logging')

    :param params: ParamDict, the constants dictionary passed in call
    :param warnlist: list of warnings, the list of warnings from
                     warnings.catch_warnings
    :param funcname: string or None, if string then also pipes "funcname" to the
                     warning message (intended to be used to identify the code/
                     function/module warning was generated in)
    :return:
    """
    # get pconstant
    pconstant = constants.pload(params['INSTRUMENT'])
    log_warnings = pconstant.LOG_CAUGHT_WARNINGS()
    # deal with warnlist as string
    if isinstance(warnlist, str):
        warnlist = [warnlist]
    # deal with warnings
    displayed_warnings = []
    if log_warnings and (len(warnlist) > 0):
        for warnitem in warnlist:

            # if we have a function name then use it else just report the
            #    line number (not recommended)
            if funcname is None:
                wargs = [warnitem.lineno, '', warnitem.message]
            else:
                wargs = [warnitem.lineno, '({0})'.format(funcname),
                         warnitem.message]
            # log message
            key = '10-005-00001'
            wmsg = textentry(key, args=wargs)
            # if we have already display this warning don't again
            if wmsg in displayed_warnings:
                continue
            else:
                wlog(params, 'warning', wmsg)
                displayed_warnings.append(wmsg)


def get_logfilepath(logobj: Logger, params: ParamDict,
                    use_group: bool = True) -> str:
    """
    Construct the log file path and filename (normally from "DRS_DATA_MSG"
    generates an DrsCodedException exception.

    "DRS_DATA_MSG" is defined in "config.py"

    :param logobj: wlog (Logger) instance
    :param params: Parameter dictionary of constants
    :param use_group: bool if True use group name in log file path

    :return lpath: string, the path and filename for the log file to be used
    :return warning: bool, if True print warnings about log file path
    """
    # -------------------------------------------------------------------------
    # deal with group
    if not use_group:
        group = None
        reset = True
    elif 'DRS_GROUP' in params:
        group = params['DRS_GROUP']
        reset = False
    else:
        group = None
        reset = False
    # -------------------------------------------------------------------------
    # get dir_data_msg key
    dir_data_msg = get_drs_data_msg(params, group, reset=reset)
    # -------------------------------------------------------------------------
    # add log file to path
    lpath = logobj.pconstant.LOG_FILE_NAME(params, dir_data_msg)
    # return the logpath and the warning
    return lpath


def correct_level(logobj: Logger, key: str, level: str):
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
        eargs = [level, func_name]
        raise DrsCodedException('00-005-00011', 'error', targs=eargs,
                                func_name=func_name)
    # get numeric value for this level
    try:
        thislevel = logobj.pconstant.WRITE_LEVEL()[key]
    except KeyError:
        eargs = [key, func_name]
        raise DrsCodedException('00-005-00012', 'error', targs=eargs,
                                func_name=func_name)
    # return whether we are printing or not
    return thislevel >= outlevel


def printlog(logobj: Logger, params: ParamDict, message: str,
             key: str = 'all', colour: str = None):
    """
    print message to stdout (if level is correct - set by PRINT_LEVEL)
    is coloured unless spirouConfig.Constants.COLOURED_LOG() is False

    :param logobj: logger instance, the logger object (for pconstant)
    :param params: ParamDict, the constants file passed in call
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
    c1, c2 = printcolour(logobj, params, key, func_name=func_name,
                         colour=colour)
    # if the colours are not None then print the message
    if c1 is not None and c2 is not None:
        print(c1 + message + c2)


def printcolour(logobj: Logger, params: ParamDict, key: str = 'all',
                func_name: Union[str, None] = None,
                colour: Union[str, None] = None) -> Tuple[str, str]:
    """
    Get the print colour (start and end) based on "key".
    This should be used as follows:
        >> c1, c2 = printcolour(key='all')
        >> print(c1 + message + c2)

    :param logobj: logger instance, the logger object (for pconstant)
    :param params: ParamDict, the constants file passed in call
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
    level = params.get('PRINT_LEVEL', 'all')
    # deal with overriding coloured text
    if colour is not None:
        colour1, colour2 = override_colour(params, colour)
        if colour1 is not None:
            return colour1, colour2
    # get the colours
    clevels = logobj.pconstant.COLOUREDLEVELS(params)
    addcolour = params.get('DRS_COLOURED_LOG', True)
    nocol = Color.ENDC
    # make sure key is in clevels
    if (key not in clevels) and addcolour:
        eargs = [level, func_name]
        raise DrsCodedException('00-005-00012', 'error', eargs,
                                func_name=func_name)

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


def override_colour(params: ParamDict, colour: str) -> Tuple[str, str]:
    """
    Override the colour with the themed colours

    :param params: ParamDict, the constants file passed in call
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
    # get theme
    if 'THEME' not in params:
        theme = 'DARK'
    else:
        theme = params['THEME']
    # get colour 1
    if theme == 'DARK':
        # find colour 1 in colour
        if colour.lower() == "red":
            colour1 = Color.RED1
        elif colour.lower() == "green":
            colour1 = Color.GREEN1
        elif colour.lower() == "blue":
            colour1 = Color.BLUE1
        elif colour.lower() == "yellow":
            colour1 = Color.YELLOW1
        elif colour.lower() == "cyan":
            colour1 = Color.CYAN1
        elif colour.lower() == "magenta":
            colour1 = Color.MAGENTA1
        elif colour.lower() == 'black':
            colour1 = Color.BLACK1
        elif colour.lower() == 'white':
            colour1 = Color.WHITE1
        else:
            colour1 = None
    # get colour 1
    else:
        # find colour 1 in colour
        if colour.lower() == "red":
            colour1 = Color.RED2
        elif colour.lower() == "green":
            colour1 = Color.GREEN2
        elif colour.lower() == "blue":
            colour1 = Color.BLUE2
        elif colour.lower() == "yellow":
            colour1 = Color.YELLOW2
        elif colour.lower() == "cyan":
            colour1 = Color.CYAN2
        elif colour.lower() == "magenta":
            colour1 = Color.MAGENTA2
        elif colour.lower() == 'black':
            colour1 = Color.BLACK2
        elif colour.lower() == 'white':
            colour1 = Color.WHITE2
        else:
            colour1 = None
    # last code should be the end
    colour2 = Color.ENDC
    # return colour1 and colour2
    return colour1, colour2


def writelog(logobj: Logger, params: ParamDict, message: str, key: str,
             logfilepath: str):
    """
    write message to log file (if level is correct - set by LOG_LEVEL)

    :param logobj: logger instance, the logger object (for pconstant)
    :param params: ParamDict, the constants file passed in call
    :param message: string, message to write to log file
    :param key: string, either "error" or "warning" or "info" or graph, this
                gives a character code in output
    :param logfilepath: string, the file name to write the log to

    :return:
    """
    func_name = __NAME__ + '.writelog()'
    # -------------------------------------------------------------------------
    # get out level key
    level = params.get('LOG_LEVEL', 'all')
    # if this level is less than out level then do not log
    if not correct_level(logobj, key, level):
        return 0
    # -------------------------------------------------------------------------
    # Check if logfile path exists
    if os.path.exists(logfilepath):
        # try to open the logfile
        try:
            # write the logfile (in access mode to append to the end)
            with open(logfilepath, 'a') as f:
                f.write(message + '\n')
        except Exception as e:
            eargs = [logfilepath, type(e), e, func_name]
            raise DrsCodedException('01-001-00011', 'error', eargs,
                                    func_name=func_name)
    else:
        # try to open the logfile
        try:
            # write the logfile (in access mode to append to the end)
            with open(logfilepath, 'a') as f:
                f.write(message + '\n')
            try:
                # change mode to rw-rw-rw-
                os.chmod(logfilepath, 0o666)
            # Pass over all OS Errors
            except OSError:
                pass
        # If we cannot write to log file then print to stdout
        except Exception as e:
            eargs = [logfilepath, type(e), e, func_name]
            raise DrsCodedException('01-001-00011', 'error', eargs,
                                    func_name=func_name)


def _clean_message(message: str) -> str:
    """
    Remove colours from a message

    :param message: str, message to clean

    :return: str, cleaned message
    """
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


def get_drs_data_msg(params: ParamDict, group: Union[str, None] = None,
                     reset: bool = False) -> str:
    """
    Get the drs message full path (either from existing one, or create one
    using group name)

    :param params: ParamDict, the parameter dictionary of constants
    :param group: str, the group name (if set)
    :param reset: bool, if True recalculates drs message full path

    :return: str, the drs message full path
    """
    # if we have a full path in params we use this
    if 'DRS_DATA_MSG_FULL' in params and not reset:
        # check that path exists - if it does skip next steps
        if params['DRS_DATA_MSG_FULL'] is None:
            pass
        elif os.path.exists(params['DRS_DATA_MSG_FULL']):
            return params['DRS_DATA_MSG_FULL']
    # ----------------------------------------------------------------------
    # get from params
    dir_data_msg = params.get('DRS_DATA_MSG', None)
    # ----------------------------------------------------------------------
    # only sort by recipe kind if group is None
    if (params['DRS_RECIPE_KIND'] is not None) and (group is None):
        kind = params['DRS_RECIPE_KIND'].lower()
        dir_data_msg = os.path.join(dir_data_msg, kind)
    # if we have a group then put it in processing folder
    elif group is not None:
        dir_data_msg = os.path.join(dir_data_msg, 'processing')
    else:
        dir_data_msg = os.path.join(dir_data_msg, 'other')
    # ----------------------------------------------------------------------
    # deal with a group directory (groups must be in sub-directory)
    if (group is not None) and (dir_data_msg is not None):
        # join to group name
        dir_data_msg = os.path.join(dir_data_msg, group)
    # ----------------------------------------------------------------------
    # add night name dir (if available) - put into sub-directory
    if ('NIGHTNAME' in params) and (dir_data_msg is not None):
        if params['NIGHTNAME'] not in [None, 'None', '']:
            dir_data_msg = os.path.join(dir_data_msg, params['NIGHTNAME'])
    # ----------------------------------------------------------------------
    # try to create directory
    if not os.path.exists(dir_data_msg):
        # noinspection PyBroadException
        try:
            os.makedirs(dir_data_msg)
        except Exception as _:
            pass
    # ----------------------------------------------------------------------
    # if None use we have to create it
    if dir_data_msg is None:
        # create default path
        create = True
    # if it doesn't exist we also have to create it
    elif not os.path.exists(dir_data_msg):
        # create default path
        create = True
    else:
        return dir_data_msg
    # ----------------------------------------------------------------------
    # if we have reached here then we need to create a default drs_data_msg
    if create:
        # get the users home directory
        homedir = os.path.expanduser('~')
        # make the default message directory
        default_msg = os.path.join(homedir, '.terrapipe_msg/')
        # check that deafult message directory exists
        if not os.path.exists(default_msg):
            # noinspection PyBroadException
            try:
                os.makedirs(default_msg)
                return default_msg
            except Exception as _:
                return './'
        else:
            return default_msg


# =============================================================================
# Define Recipe Log functions
# =============================================================================


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
    testwlog = wlog
    # Title test
    testwlog(pp, '', ' *****************************************')
    testwlog(pp, '', ' * TEST @(#) Some Observatory (' + 'V0.0.-1' + ')')
    testwlog(pp, '', ' *****************************************')
    # info log
    testwlog(pp, 'info', "This is an info test")
    # warning log
    testwlog(pp, 'warning', "This is a warning test")
    # error log
    testwlog(pp, 'error', "This is an error test")

# =============================================================================
# End of code
# =============================================================================

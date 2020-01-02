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
from astropy.table import Table
from collections import OrderedDict

from apero.core.instruments.default import pseudo_const
from apero.core import constants
from apero.locale import drs_text
from apero.locale import drs_exceptions
from apero.core.math import time


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_log.py'
__INSTRUMENT__ = 'None'
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
TextEntry = drs_text.TextEntry
TextDict = drs_text.TextDict
HelpEntry = drs_text.HelpEntry
HelpText = drs_text.HelpDict
# get the default language
DEFAULT_LANGUAGE = drs_text.DEFAULT_LANGUAGE
# Get the Color dict
Color = pseudo_const.Colors
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
            self.instrument = paramdict.get('INSTRUMENT', None)
            self.language = paramdict.get('LANGUAGE', 'ENG')
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
        self.textdict = TextDict(self.instrument, self.language)
        self.helptext = HelpText(self.instrument, self.language)
        self.d_textdict = TextDict(self.instrument, DEFAULT_LANGUAGE)
        self.d_helptext = HelpText(self.instrument, DEFAULT_LANGUAGE)
        # ---------------------------------------------------------------------
        # save output parameter dictionary for saving to file
        self.pout = ParamDict()
        # get log storage keys
        storekey = self.pconstant.LOG_STORAGE_KEYS()
        # add log stats to pout
        for key in storekey:
            self.pout[storekey[key]] = []
        self.pout['LOGGER_FULL'] = []

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
        func_name = __NAME__ + '.Logger.__call__()'
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
        # deal with message format (convert to TextEntry)
        if message is None:
            msg_obj = TextEntry('Unknown')
        elif type(message) is str:
            msg_obj = TextEntry(message)
        elif type(message) is list:
            msg_obj = TextEntry(message[0])
            for msg in message[1:]:
                msg_obj += TextEntry(msg)
        elif type(message) is TextEntry:
            msg_obj = message
        elif type(message) is HelpEntry:
            msg_obj = message.convert(TextEntry)
        else:
            msg_obj = TextEntry('00-005-00001', args=[message])
            key = 'error'
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
            msg_obj += TextEntry('00-005-00002', args=eargs)
            key = 'error'
        if key not in self.pconstant.WRITE_LEVEL():
            eargs = [key, 'WRITE_LEVEL()']
            msg_obj += TextEntry('00-005-00003', args=eargs)
            key = 'error'
        if key not in self.pconstant.COLOUREDLEVELS():
            eargs = [key, 'COLOUREDLEVELS()']
            msg_obj += TextEntry('00-005-00004', args=eargs)
            key = 'error'
        if key not in self.pconstant.REPORT_KEYS():
            eargs = [key, 'REPORT_KEYS()']
            msg_obj += TextEntry('00-005-00005', args=eargs)
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
        if type(message) is HelpEntry:
            raw_message1 = msg_obj.get(self.helptext, report=report,
                                       reportlevel=key)
        else:
            raw_message1 = msg_obj.get(self.textdict, report=report,
                                       reportlevel=key)
        # split by '\n'
        raw_messages1 = raw_message1.split('\n')
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
                    new_messages = textwrap(mess, char_len)
                    for new_message in new_messages:
                        # add a space to the start of messages (if not present)
                        if not new_message.startswith(' '):
                            new_message = ' ' + new_message
                        cmdargs = [human_time, code, option, new_message]
                        cmd = LOGFMT.format(*cmdargs)
                        # append separate commands for log writing
                        cmds.append(cmd)
                        # add to logger storage
                        self.logger_storage(params, key, human_time,
                                            new_message, printonly)
                        # print to stdout
                        printlog(self, params, cmd, key, colour)
                else:
                    cmdargs = [human_time, code, option, mess]
                    cmd = LOGFMT.format(*cmdargs)
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
        report = self.pconstant.REPORT_KEYS().get(key, False)
        # get messages
        if type(message) is HelpEntry:
            raw_message2 = msg_obj.get(self.d_helptext, report=True,
                                       reportlevel=key)
        else:
            raw_message2 = msg_obj.get(self.d_textdict, report=True,
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
            self.textdict = TextDict(self.instrument, self.language)
            self.helptext = HelpText(self.instrument, self.language)

    def output_param_dict(self, paramdict, new=False):
        func_name = __NAME__ + '.Logger.output_param_dict()'
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
        if 'LOGGER_FULL' in self.pout[pid]:
            self.pout[pid]['LOGGER_FULL'].append([[ttime, mess]])
        else:
            self.pout[pid]['LOGGER_FULL'] = [[ttime, mess]]

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

    def printmessage(self, params, messages, colour=None):
        # check whether message is string (if so make a list)
        if isinstance(messages, str):
            messages = [messages]
        # loop around messages
        for message in messages:
            printlog(self, params, message, key='all', colour=colour)

    def logmessage(self, params, messages):
        # get logfilepath
        logfilepath = get_logfilepath(self, params)
        # check whether message is string (if so make a list)
        if isinstance(messages, str):
            messages = [messages]
        # loop around messages
        for message in messages:
            writelog(self, params, message, key='all', logfilepath=logfilepath)


class Printer():
    """Print things to stdout on one line dynamically"""
    def __init__(self, params, level, message):
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


class RecipeLog:

    def __init__(self, name, params, level=0):
        # get the recipe name
        self.name = str(name)
        self.kind = str(params['DRS_RECIPE_KIND'])
        self.defaultpath = str(params['DRS_DATA_MSG_FULL'])
        self.logfitsfile = str(params['DRS_LOG_FITS_NAME'])
        self.inputdir = str(params['INPATH'])
        self.outputdir = str(params['OUTPATH'])
        # set the pid
        self.pid = str(params['PID'])
        self.htime = str(params['DATE_NOW'])
        self.group = str(params['DRS_GROUP'])
        # set the night name directory
        self.directory = str(params['NIGHTNAME'])
        # get lof fits path
        self.logfitspath = self._get_write_dir()
        # define lockfile (we need to lock the directory while this is
        #   being done)
        self.lockfile = self.directory + '_log'
        # set the log file name
        self.log_file = 'None'
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
        self.qc_value = ''
        # set the errors
        self.errors = ''
        # set that recipe ended
        self.ended = False
        # set lock function
        self.lfunc = None

    def copy(self, rlog):
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

    def set_log_file(self, logfile):
        self.log_file = logfile

    def set_inputs(self, params, rargs, rkwargs, rskwargs):
        # deal with not having inputs
        if 'INPUTS' not in params:
            return
        # get inputs
        inputs = params['INPUTS']
        # start run string
        if self.name.endswith('.py'):
            self.runstring = '{0} '.format(self.name)
        else:
            self.runstring = '{0}.py '.format(self.name)
        # ------------------------------------------------------------------
        # deal with arguments
        self.args = self._input_str(inputs, rargs, kind='arg')
        # ------------------------------------------------------------------
        # deal with kwargs
        self.kwargs = self._input_str(inputs, rkwargs, kind='kwargs')
        # ------------------------------------------------------------------
        # deal with special kwargs
        self.skwargs = self._input_str(inputs, rskwargs, kind='skwargs')
        # strip the runstring
        self.runstring.strip()

    def set_lock_func(self, func):
        self.lfunc = func

    def add_level(self, params, key, value, write=True):
        # get new level
        level = self.level + 1
        # create new log
        newlog = RecipeLog(self.name, params, level=level)
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

    def add_qc(self, params, qc_params, passed, write=True):
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
            # deal with qc set
            qargs = [qc_names[it], qc_values[it], qc_logic[it]]
            self.qc_value += '{0}={1} ({2})'.format(*qargs)

        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def no_qc(self, params, write=True):
        self.passed_qc = True
        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def add_error(self, params, errortype, errormsg, write=True):
        self.errors += '"{0}":"{1}" '.format(errortype, errormsg)
        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def end(self, params, write=True):

        self.ended = True
        # whether to write (update) recipe log file
        if write:
            self.write_logfile(params)

    def write_logfile(self, params):
        if self.lfunc is None:
            return 0
        else:
            return self.lfunc(params, self.lockfile, self._writer)

    def _input_str(self, inputs, argdict, kind='arg'):
        # setup input str
        inputstr = ''
        # deal with kind
        if kind == 'arg':
            prefix = ''
        else:
            prefix = '--'
        # deal with arguments
        for argname in argdict:
            # get arg
            arg = argdict[argname]
            # strip prefix (may or may not have one)
            argname = argname.strip(prefix)
            # get input arg
            iarg = inputs[argname.strip(prefix)]
            # add prefix (add prefix whether it had one or not)
            argname = prefix + argname
            # deal with file arguments
            if arg.dtype in ['file', 'files']:
                if not isinstance(iarg, list):
                    continue
                # get string and drsfile
                strfiles = iarg[0]
                drsfiles = iarg[1]
                # deal with having string (force to list)
                if isinstance(strfiles, str):
                    strfiles = [strfiles]
                    drsfiles = [drsfiles]

                # add argname to run string
                if kind != 'arg':
                    self.runstring += '{0} '.format(argname)
                # loop around fiels and add them
                for f_it in range(len(strfiles)):
                    # add to list
                    fargs = [argname, f_it, strfiles[f_it], drsfiles[f_it].name]
                    inputstr += '{0}[1]={2}[{3}] '.format(*fargs)
                    # add to run string
                    if strfiles[f_it] in ['None', None, '']:
                        continue
                    else:
                        basefile = os.path.basename(strfiles[f_it])
                        self.runstring += '{0} '.format(basefile)
            else:
                inputstr += '{0}={1} '.format(argname, iarg)
                # skip Nones
                if iarg in ['None', None, '']:
                    continue
                # add to run string
                if isinstance(iarg, str):
                    iarg = os.path.basename(iarg)
                if kind != 'arg':
                    self.runstring += '{0}={1} '.format(argname, iarg)
                else:
                    self.runstring += '{0} '.format(iarg)

        # return the input string
        return inputstr.strip()

    # private methods
    def _get_write_dir(self):
        # ------------------------------------------------------------------
        # get log path
        if self.outputdir not in ['None', '', None]:
            path = self.outputdir
            # if we have a night name add it
            if self.directory not in ['None', '', None]:
                path = os.path.join(path, self.directory)
        # else use the default path
        else:
            path = self.defaultpath
        # ------------------------------------------------------------------
        # check that directory exists
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                # TODO: move to language database
                emsg = 'RecipeLogError: Cannot make path {0} for recipe log.'
                eargs = [path]
                raise DrsError(emsg.format(*eargs))
        # ------------------------------------------------------------------
        # return absolute log file path
        return os.path.join(path, self.logfitsfile)

    def _make_row(self):
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
        row['RUNSTRING'] = self.runstring
        row['ARGS'] = self.args
        row['KWARGS'] = self.kwargs
        row['SKWARGS'] = self.skwargs
        row['STARTED'] = self.started
        row['PASSED_QC'] = self.passed_qc
        row['QC_VALUES'] = self.qc_value
        row['ERRORS'] = self.errors
        row['ENDED'] = self.ended
        return row

    def _get_rows(self):
        rows = []
        # case where we have no sets
        if len(self.set) == 0:
            rows.append(self._make_row())
        else:
            # else we have children
            for child in self.set:
                rows += child._get_rows()
        # return rows
        return rows

    def _writer(self):
        # get write path
        writepath = self.logfitspath
        # ------------------------------------------------------------------
        # check to see if table already exists
        if os.path.exists(writepath):
            try:
                print('RecipeLog: Reading file: {0}'.format(writepath))
                table = Table.read(writepath)
            except Exception as e:
                # TODO: move to language database
                emsg = 'RecipeLogError: Cannot read file {0} \n\t {1}: {2}'
                eargs = [writepath, type(e), str(e)]
                raise DrsError(emsg.format(*eargs))
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
        rows = self._get_rows()
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
            print('RecipeLog: Writing file: {0}'.format(writepath))
            mastertable.write(writepath, format='fits', overwrite=True)
        except Exception as e:
            # TODO: move to language database
            emsg = 'RecipeLogError: Cannot write file {0} \n\t Error {1}: {2}'
            eargs = [writepath, type(e), str(e)]
            raise DrsError(emsg.format(*eargs))


# =============================================================================
# Define our instance of wlog
# =============================================================================
# Get our instance of logger
wlog = Logger()


# =============================================================================
# Define Logger functions
# =============================================================================
def find_param(params=None, key=None, name=None, kwargs=None, func=None,
               mapf=None, dtype=None, paramdict=None, required=True,
               default=None):
    # deal with params being None
    if params is None:
        params = ParamDict()
    # deal with dictionary being None
    if paramdict is None:
        paramdict = params
    else:
        paramdict = ParamDict(paramdict)
    # deal with key being None
    if key is None and name is None:
        wlog(params, 'error', TextEntry('00-003-00004'))
    elif key is None:
        key = 'Not set'
    # deal with no kwargs
    if kwargs is None:
        rkwargs = dict()
    else:
        rkwargs = dict()
        # force all kwargs to be upper case
        for kwarg in kwargs:
            rkwargs[kwarg.upper()] = kwargs[kwarg]
    # deal with no function
    if func is None:
        func = 'UNKNOWN'
    # deal with no name
    if name is None:
        name = key.upper()
    else:
        name = name.upper()

    # deal with None in rkwargs (take it as being unset)
    if name in rkwargs:
        if rkwargs[name] is None:
            del rkwargs[name]
    # deal with key not found in params
    not_in_paramdict = name not in rkwargs
    not_in_rkwargs = key not in paramdict
    return_default = (not required) or (default is not None)
    # if we don't require value
    if return_default and not_in_paramdict and not_in_rkwargs:
        return default
    elif not_in_paramdict and not_in_rkwargs:
        eargs = [key, func]
        wlog(params, 'error', TextEntry('00-003-00001', args=eargs))
        return default
    elif name in rkwargs:
        return rkwargs[name]
    elif mapf == 'list':
        return paramdict.listp(key, dtype=dtype)
    elif mapf == 'dict':
        return paramdict.dictp(key, dtype=dtype)
    else:
        return paramdict[key]


def printlogandcmd(logobj, params, message, key, human_time, option, wrap,
                   colour):
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
        message = [logobj.textdict['00-005-00005'].format(message)]
        key = 'error'
    for mess in message:
        code = logobj.pconstant.LOG_TRIG_KEYS().get(key, ' ')
        # check if line is over 80 chars
        if (len(mess) > char_len) and wrap:
            # get new messages (wrapped at CHAR_LEN)
            new_messages = textwrap(mess, char_len)
            for new_message in new_messages:
                cmdargs = [human_time, code, option, new_message]
                cmd = LOGFMT.format(*cmdargs)
                printlog(logobj, params, cmd, key, colour)
        else:
            cmdargs = [human_time, code, option, mess]
            cmd = LOGFMT.format(*cmdargs)
            printlog(logobj, params, cmd, key, colour)


def debug_start(logobj, params, raise_exception):
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
    text = logobj.textdict
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
                logobj.pconstant.EXIT(params)()
        elif '2' in uinput.upper():
            print(cc + text['00-005-00009'] + nocol)

            import pdb
            pdb.set_trace()

            print(cc + text['00-005-00010'] + nocol)
            if raise_exception:
                logobj.pconstant.EXIT(params)()
        elif raise_exception:
            logobj.pconstant.EXIT(params)()
    except:
        if raise_exception:
            logobj.pconstant.EXIT(params)()


def display_func(params=None, name=None, program=None, class_name=None):
    func_name = __NAME__ + '.display_func()'
    # start the string function
    strfunc = ''
    # deal with no file name
    if name is None:
        name = 'Unknown'
    # add brackets to show function
    if not name.endswith('()'):
        name += '()'
    # add the program
    if program is not None:
        strfunc = str(program)
    if class_name is not None:
        strfunc += '.{0}'.format(class_name)
    # add the name
    strfunc += '.{0}'.format(name)
    # deal with no params (do not log)
    if params is None:
        return strfunc
    # deal with debug level too low (just return here)
    if params['DRS_DEBUG'] < params['DEBUG_MODE_FUNC_PRINT']:
        return strfunc
    # ----------------------------------------------------------------------
    # below here just for debug mode func print
    # ----------------------------------------------------------------------
    # add the string function to param dict
    if 'DEBUG_FUNC_LIST' not in params:
        params.set('DEBUG_FUNC_LIST', value=[None], source=func_name)
    if 'DEBUG_FUNC_DICT' not in params:
        params.set('DEBUG_FUNC_DICT', value=dict(), source=func_name)
    # append to list
    params['DEBUG_FUNC_LIST'].append(strfunc)
    # update debug dictionary
    if strfunc in params['DEBUG_FUNC_DICT']:
        params['DEBUG_FUNC_DICT'][strfunc] += 1
    else:
        params['DEBUG_FUNC_DICT'][strfunc] = 1
    # get count
    count = params['DEBUG_FUNC_DICT'][strfunc]
    # find previous entry
    previous = params['DEBUG_FUNC_LIST'][-2]
    # find out whether we have the same entry
    same_entry = previous == strfunc
    # add count
    strfunc += ' (N={0})'.format(count)
    # if we don't have a list then just print
    if params['DEBUG_FUNC_LIST'][-2] is None:
        # log in func
        wlog(params, 'debug', TextEntry('90-000-00004', args=[strfunc]),
             wrap=False)
    elif not same_entry:
        # get previous set of counts
        previous_count = _get_prev_count(params, previous)
        # only log if count is greater than 1
        if previous_count > 1:
            # log how many of previous there were
            dargs = [previous_count]
            wlog(params, 'debug', TextEntry('90-000-00005', args=dargs))
        # log in func
        wlog(params, 'debug', TextEntry('90-000-00004', args=[strfunc]),
             wrap=False)

    # return func_name
    return strfunc


def _get_prev_count(params, previous):
    # get the debug list
    debug_list = params['DEBUG_FUNC_LIST'][:-1]
    # get the number of iterations
    n_elements = 0
    # loop around until we get to
    for row in range(len(debug_list))[::-1]:
        if debug_list[row] != previous:
            break
        else:
            n_elements += 1
    # return number of element founds
    return n_elements


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
    textdict = TextDict(p['INSTRUMENT'], p['LANGUAGE'])

    # get pconstant
    pconstant = constants.pload(p['INSTRUMENT'])
    log_warnings = pconstant.LOG_CAUGHT_WARNINGS()

    # deal with warnings
    displayed_warnings = []
    if log_warnings and (len(w) > 0):
        for wi in w:
            # if we have a function name then use it else just report the
            #    line number (not recommended)
            if funcname is None:
                wargs = [wi.lineno, '', wi.message]
            else:
                wargs = [wi.lineno, '({0})'.format(funcname), wi.message]
            # log message
            key = '10-005-00001'
            wmsg = textdict[key].format(*wargs)
            # if we have already display this warning don't again
            if wmsg in displayed_warnings:
                continue
            else:
                wlog(p, 'warning', TextEntry(key, args=wargs))
                displayed_warnings.append(wmsg)


def get_logfilepath(logobj, params, use_group=True):
    """
    Construct the log file path and filename (normally from "DRS_DATA_MSG"
    generates an ConfigError exception.

    "DRS_DATA_MSG" is defined in "config.py"

    :return lpath: string, the path and filename for the log file to be used
    :return warning: bool, if True print warnings about log file path
    """
    # -------------------------------------------------------------------------
    # deal with group
    if not use_group:
        group = None
    elif 'DRS_GROUP' in params:
        group = params['DRS_GROUP']
    else:
        group = None
    # -------------------------------------------------------------------------
    # get dir_data_msg key
    dir_data_msg = get_drs_data_msg(params, group)
    # -------------------------------------------------------------------------
    # add log file to path
    lpath = logobj.pconstant.LOG_FILE_NAME(params, dir_data_msg)
    # return the logpath and the warning
    return lpath


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
        emsg = TextEntry('00-005-00011', args=[level, func_name])
        raise ConfigError(errorobj=[emsg, logobj.textdict])

    # get numeric value for this level
    try:
        thislevel = logobj.pconstant.WRITE_LEVEL()[key]
    except KeyError:
        emsg = TextEntry('00-005-00012', args=[key, func_name])
        raise ConfigError(errorobj=[emsg, logobj.textdict])

    # return whether we are printing or not
    return thislevel >= outlevel


def printlog(logobj, params, message, key='all', colour=None):
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


def textwrap(input_string, length):
    return constants.constant_functions.textwrap(input_string, length)


def printcolour(logobj, params, key='all', func_name=None, colour=None):
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
        emsg = TextEntry('00-005-00012', args=[level, func_name])
        raise ConfigError(errorobj=[emsg, logobj.textdict])

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


def override_colour(params, colour):
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

    # get the colour codes
    codes = Color
    # get theme
    if 'THEME' not in params:
        theme = 'DARK'
    else:
        theme = params['THEME']
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


def writelog(logobj, params, message, key, logfilepath):
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
            # open/write and close the logfile
            f = open(logfilepath, 'a')
            f.write(message + '\n')
            f.close()
        except Exception as e:
            eargs = [logfilepath, type(e), e, func_name]
            emsg = TextEntry('01-001-00011', args=eargs)
            raise ConfigError(errorobj=[emsg, logobj.textdict])
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
            emsg = TextEntry('01-001-00011', args=eargs)
            raise ConfigError(errorobj=[emsg, logobj.textdict])


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


def get_drs_data_msg(params, group=None, reset=False):
    # if we have a full path in params we use this
    if 'DRS_DATA_MSG_FULL' in params and not reset:
        # check that path exists - if it does skip next steps
        if os.path.exists(params['DRS_DATA_MSG_FULL']):
            return params['DRS_DATA_MSG_FULL']
    # ----------------------------------------------------------------------
    # get from params
    dir_data_msg = params.get('DRS_DATA_MSG', None)
    # ----------------------------------------------------------------------
    # only sort by recipe kind if group is None
    if ('DRS_RECIPE_KIND' is not None) and (group is None):
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
        try:
            os.makedirs(dir_data_msg)
        except Exception:
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

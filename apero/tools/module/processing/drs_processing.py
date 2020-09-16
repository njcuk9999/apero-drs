#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-06 at 11:57

@author: cook
"""
import numpy as np
import os
import sys
from copy import deepcopy
import time
from astropy.table import Table
from collections import OrderedDict
import multiprocessing
from multiprocessing import Pool, Process, Manager, Event
from typing import List, Tuple, Union

from apero.base import base
from apero.base import drs_base_classes as base_class
from apero.base import drs_exceptions
from apero.base import drs_text
from apero.core.core import drs_log
from apero.core.utils import drs_recipe, drs_startup
from apero import lang
from apero.core import constants
from apero import plotting
from apero.io import drs_table
from apero.io import drs_lock
from apero.tools.module.setup import drs_reset
from apero.science import telluric


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.processing.drs_processing.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)

# Run keys
RUN_KEYS = dict()
RUN_KEYS['RUN_NAME'] = 'Run Unknown'
RUN_KEYS['SEND_EMAIL'] = False
RUN_KEYS['EMAIL_ADDRESS'] = None
RUN_KEYS['NIGHTNAME'] = None
RUN_KEYS['BNIGHTNAMES'] = None
RUN_KEYS['WNIGHTNAMES'] = None
RUN_KEYS['PI_NAMES'] = None
RUN_KEYS['MASTER_NIGHT'] = None
RUN_KEYS['CORES'] = 1
RUN_KEYS['STOP_AT_EXCEPTION'] = False
RUN_KEYS['TEST_RUN'] = False
RUN_KEYS['TRIGGER_RUN'] = False
RUN_KEYS['ENGINEERING'] = False
RUN_KEYS['RESET_ALLOWED'] = False
RUN_KEYS['RESET_TMP'] = False
RUN_KEYS['RESET_REDUCED'] = False
RUN_KEYS['RESET_CALIB'] = False
RUN_KEYS['RESET_TELLU'] = False
RUN_KEYS['RESET_LOG'] = False
RUN_KEYS['RESET_PLOT'] = False
RUN_KEYS['RESET_RUN'] = False
RUN_KEYS['RESET_LOGFITS'] = False
RUN_KEYS['TELLURIC_TARGETS'] = None
RUN_KEYS['SCIENCE_TARGETS'] = None
# storage for reporting removed engineering directories
REMOVE_ENG_NIGHTS = []
# get special list from recipes
SPECIAL_LIST_KEYS = drs_recipe.SPECIAL_LIST_KEYS
# get list of obj name cols
OBJNAMECOLS = ['KW_OBJNAME']
# list of arguments to remove from skip check
SKIP_REMOVE_ARGS = ['--skip', '--program', '--debug', '--plot', '--master']


# =============================================================================
# Define classes
# =============================================================================
class Run:
    def __init__(self, params, runstring,
                 mod: Union[base_class.ImportModule, None] = None,
                 priority=0, inrecipe=None):
        self.params = params
        self.pconst = constants.pload(params['INSTRUMENT'])
        self.runstring = runstring
        self.priority = priority
        self.args = []
        self.recipename = ''
        self.runname = None
        self.skipname = None
        self.recipe = inrecipe
        if mod is not None:
            self.module = mod.copy()
        else:
            self.module = None
        self.master = False
        self.recipemod = None
        self.kwargs = dict()
        self.fileargs = dict()
        self.required_args = []
        # set parameters
        self.kind = None
        self.nightname = None
        # update parameters given runstring
        self.update()

    def filename_args(self):
        """
        deal with file arguments in kwargs (returned from recipe_setup as
            [filenames, file instances]

        we only want the filenames (not the instances)

        :return:
        """
        # loop around positional arguments
        for argname in self.recipe.args:
            # get arg instance
            arg = self.recipe.args[argname]
            # only do this for arguments with filetype 'files' or 'file'
            if arg.dtype in ['files', 'file']:
                self.kwargs[argname] = self.kwargs[argname][0]
        # loop around optional arguments
        for kwargname in self.recipe.kwargs:
            # get arg instance
            kwarg = self.recipe.kwargs[kwargname]
            # only do this for arguments with filetype 'files' or 'file'
            if kwarg.dtype in ['files', 'file']:
                # deal with arguments that are required:
                #   - always = kwarg.required
                #   - for reprocessing = kwarg.reprocessing
                if kwarg.required or kwarg.reprocess:
                    # if we have no arguments then as they are required we
                    #   need to give a blank list (this will then have to be
                    #   handled by recipes where this is the case -
                    #   for kwargs.required this will be an error
                    #   for kwargs.reprocess the recipe must deal with a blank
                    #   set of files for this argument
                    if len(self.kwargs[kwargname]) == 0:
                        self.kwargs[kwargname] = []
                    # else we have arguments (user does not enter the
                    #     DrsFitsFile instance therefore we just keep the
                    #     string filename
                    else:
                        self.kwargs[kwargname] = self.kwargs[kwargname][0]
                # else we do not require the files options thus we need to sort
                #   through possible options
                else:
                    # option 1: the argument is None --> del argument
                    if drs_text.null_text(self.kwargs[kwargname], ['None']):
                        del self.kwargs[kwargname]
                    # option 2: the argument is empty --> del argument
                    elif len(self.kwargs[kwargname]) == 0:
                        del self.kwargs[kwargname]
                    # option 3: we have an arugment --> use argument (but
                    #           remove DrsFitsFile instance - we only need the
                    #           string filename
                    else:
                        self.kwargs[kwargname] = self.kwargs[kwargname][0]

    def find_recipe(self, mod=None) -> Tuple[drs_recipe.DrsRecipe,
                                       base_class.ImportModule]:
        """

        :param mod: Module
        :return:
        :rtype: Tuple[DrsRecipe, Module]
        """
        # find the recipe definition
        recipe, mod = drs_startup.find_recipe(self.recipename,
                                              self.params['INSTRUMENT'],
                                              mod=mod)
        # deal with an empty recipe return
        if recipe.name == 'Empty':
            eargs = [self.recipename]
            WLOG(None, 'error', TextEntry('00-007-00001', args=eargs))
        # else return
        return recipe, mod

    def get_recipe_kind(self):
        # the first argument must be the recipe name
        self.recipename = self.args[0]
        # make sure recipe does not have .py on the end
        self.recipename = _remove_py(self.recipename)
        # get recipe type (raw/tmp/reduced)
        if self.recipe.inputdir == 'raw':
            self.kind = 0
        elif self.recipe.inputdir == 'tmp':
            self.kind = 1
        elif self.recipe.inputdir == 'reduced':
            self.kind = 2
        else:
            emsg1 = ('RunList Error: Recipe = "{0}" invalid'
                     ''.format(self.recipename))
            emsg2 = '\t Line: {0} {1}'.format(self.priority, self.runstring)
            WLOG(self.params, 'error', [emsg1, emsg2])
            self.kind = -1

    def get_night_name(self):
        if 'directory' in self.recipe.args:
            # get directory position
            pos = int(self.recipe.args['directory'].pos) + 1
            # set
            self.nightname = self.args[pos]
        else:
            self.nightname = ''

    def update(self):
        # get args
        self.args = self.runstring.split(' ')
        # the first argument must be the recipe name
        self.recipename = self.args[0]
        # find the recipe
        if self.recipe is None:
            self.recipe, self.module = self.find_recipe(self.module)
            # get filemod and recipe mod
            self.recipe.filemod = self.pconst.FILEMOD()
        # import the recipe module
        self.recipemod = self.recipe.main
        # turn off the input validation
        self.recipe.input_validation = False
        # get the master setting
        self.master = self.recipe.master
        # run parser with arguments
        self.kwargs = self.recipe.recipe_setup(inargs=self.args)
        # add argument to set program name
        pargs = [self.recipe.shortname, int(self.priority)]
        self.kwargs['program'] = '{0}[{1:05d}]'.format(*pargs)
        # deal with file arguments in kwargs (returned from recipe_setup as
        #    [filenames, file instances]
        self.filename_args()
        # turn on the input validation
        self.recipe.input_validation = True
        # sort out names
        self.shortname = self.recipe.shortname
        self.runname = 'RUN_{0}'.format(self.shortname)
        self.skipname = 'SKIP_{0}'.format(self.shortname)
        # get properties
        self.get_recipe_kind()
        self.get_night_name()
        # populate a list of reciped arguments
        for kwarg in self.recipe.kwargs:
            if self.recipe.kwargs[kwarg].required:
                self.required_args.append(kwarg)


    def prerun_test(self):
        """
        Just before running test that all files required are present
        Due to the way users can skip tests this is needed and this
        knowledge will not be known apriori

        :return:
        """
        # get params and recipe
        params, recipe = self.params, self.recipe
        # ------------------------------------------------------------------
        # get the input directory
        input_dir = recipe.get_input_dir()
        # check whether input directory exists
        if not os.path.exists(input_dir):
            wargs = [input_dir]
            WLOG(params, 'warning', TextEntry('10-503-00008', args=wargs))
            return False
        # ------------------------------------------------------------------
        # if we have a directory add it to the input dir
        if 'directory' in self.kwargs:
            input_dir = os.path.join(input_dir, self.kwargs['directory'])
            # check whether directory exists (if present)
            if not os.path.exists(input_dir):
                wargs = [self.kwargs['directory'], input_dir]
                WLOG(params, 'warning', TextEntry('10-503-00009', args=wargs))
                return False
        # ------------------------------------------------------------------
        # loop around positional arguments
        for argname in recipe.args:
            # skip if not present in kwargs
            if argname not in self.kwargs:
                continue
            # get arg instance
            arg = recipe.args[argname]
            # only do this for arguments with filetype 'files' or 'file'
            if arg.dtype in ['files', 'file']:
                files = self.kwargs[argname]
                # make sure we have a list of files
                if not isinstance(files, list):
                    files = [files]
                # loop around files
                for filename in files:
                    # construct path
                    abspath = os.path.join(input_dir, filename)
                    # check if path exists
                    if not os.path.exists(abspath):
                        # log warning
                        wargs = [argname, abspath]
                        wmsg = TextEntry('10-503-00010', args=wargs)
                        WLOG(params, 'warning', wmsg)
                        return False
        # ------------------------------------------------------------------
        # loop around optional arguments
        for kwargname in self.recipe.kwargs:
            # skip if not present in kwargs
            if kwargname not in self.kwargs:
                continue
            # get arg instance
            kwarg = self.recipe.kwargs[kwargname]
            # only do this for arguments with filetype 'files' or 'file'
            if kwarg.dtype in ['files', 'file']:
                files = self.kwargs[kwargname]
                # make sure we have a list of files
                if not isinstance(files, list):
                    files = [files]
                # loop around files
                for filename in files:
                    # construct path
                    abspath = os.path.join(input_dir, filename)
                    # check if path exists
                    if not os.path.exists(abspath):
                        # log warning
                        wargs = [kwargname, abspath]
                        wmsg = TextEntry('10-503-00010', args=wargs)
                        WLOG(params, 'warning', wmsg)
                        return False
        # ------------------------------------------------------------------
        # if all have passed we return True
        return True

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Run[{0}]'.format(self.runstring)


# =============================================================================
# Define user functions
# =============================================================================
def run_process(params, recipe, module, *gargs, terminate=False, **gkwargs):
    # generate run table (dictionary from reprocessing)
    runtable = generate_run_table(params, module, *gargs, **gkwargs)
    # Generate run list
    rlist = generate_run_list(params, None, runtable, None)
    # Process run list
    outlist, has_errors = process_run_list(params, recipe, rlist)
    # display errors
    if has_errors:
        # terminate here
        if terminate:
            display_errors(params, outlist)
            eargs = [module.name, recipe.name]
            WLOG(params, 'error', TextEntry('00-001-00043', args=eargs))
        else:
            eargs = [module.name, recipe.name]
            WLOG(params, 'warning', TextEntry('00-001-00043', args=eargs))
    # return outlist
    return outlist


def combine_outlist(name, goutlist, outlist):
    # loop around keys in outlist
    for key in outlist:
        # construct new unique key using name
        newkey = '{0}_{1}'.format(name, key)
        # add to global outlist
        goutlist[newkey] = outlist[key]
    # return global outlist
    return goutlist


def read_runfile(params, runfile, **kwargs):
    func_name = __NAME__ + '.read_runfile()'
    # ----------------------------------------------------------------------
    # get properties from params
    run_key = pcheck(params, 'REPROCESS_RUN_KEY', 'run_key', kwargs, func_name)
    run_dir = pcheck(params, 'DRS_DATA_RUN', 'run_dir', kwargs, func_name)
    # ----------------------------------------------------------------------
    # check if run file exists
    if not os.path.exists(runfile):
        # construct run file
        runfile = os.path.join(run_dir, runfile)
        # check that it exists
        if not os.path.exists(runfile):
            WLOG(params, 'error', TextEntry('09-503-00002', args=[runfile]))
    # ----------------------------------------------------------------------
    # try to fix file
    fix_run_file(runfile)
    # ----------------------------------------------------------------------
    # now try to load run file
    try:
        keys, values = np.genfromtxt(runfile, delimiter='=', comments='#',
                                     unpack=True, dtype=str)
    except Exception as e:
        # log error
        eargs = [runfile, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('09-503-00003', args=eargs))
        keys, values = [], []
    # ----------------------------------------------------------------------
    # table storage
    runtable = OrderedDict()
    keytable = OrderedDict()
    # ----------------------------------------------------------------------
    # unlock params
    params.unlock()
    # ----------------------------------------------------------------------
    # sort out keys into id keys and values for params
    for it in range(len(keys)):
        # get this iterations values
        key = keys[it].upper().strip()
        value = values[it].strip()
        # find the id keys
        if key.startswith(run_key):
            # attempt to read id string
            try:
                runid = int(key.replace(run_key, ''))
            except Exception as e:
                eargs = [key, value, run_key, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('09-503-00004', args=eargs))
                runid = None
            # check if we already have this column
            if runid in runtable:
                wargs = [runid, keytable[runid], runtable[runid],
                         keys[it], values[it][:40] + '...']
                WLOG(params, 'warning', TextEntry('10-503-00001', args=wargs))
            # add to table
            runtable[runid] = value
            keytable[runid] = key
        # else add to parameter dictionary
        else:
            # deal with special strings
            if value.upper() == 'TRUE':
                value = True
            elif value.upper() == 'FALSE':
                value = False
            elif value.upper() == 'NONE':
                value = None
            # log if we are overwriting value
            if (key in params):
                wargs = [key, params[key], value]
                WLOG(params, 'warning', TextEntry('10-503-00002', args=wargs))
            # add to params
            params[key] = value
            params.set_source(key, func_name)
    # ----------------------------------------------------------------------
    # push default values (incase we don't have values in run file
    for key in RUN_KEYS:
        if key not in params:
            # warning that we are using default settings
            wargs = [key, RUN_KEYS[key]]
            WLOG(params, 'warning', TextEntry('10-503-00005', args=wargs))
            # push keys to params
            params[key] = RUN_KEYS[key]
            params.set_source(key, __NAME__ + '.RUN_KEYS')

    # ----------------------------------------------------------------------
    # deal with arguments from command line (params['INPUTS'])
    # ----------------------------------------------------------------------
    # nightname
    if 'NIGHTNAME' in params['INPUTS']:
        # get night name
        _nightname = params['INPUTS']['NIGHTNAME']
        # deal with none nulls
        if not drs_text.null_text(_nightname, ['None', '', 'All']):
            params['NIGHTNAME'] = _nightname
    # make sure nightname is str or None
    if drs_text.null_text(params['NIGHTNAME'], ['None', '', 'All']):
        params['NIGHTNAME'] = None
    # ----------------------------------------------------------------------
    # nightname blacklist
    if 'BNIGHTNAMES' in params['INPUTS']:
        # get night name blacklist
        _bnightnames = params['INPUTS']['BNIGHTNAMES']
        # deal with non-null value
        if not drs_text.null_text(_bnightnames, ['None', '', 'All']):
            params['BNIGHTNAMES'] = params['INPUTS'].listp('BNIGHTNAMES')
    # ----------------------------------------------------------------------
    # nightname whitelist
    if 'WNIGHTNAMES' in params['INPUTS']:
        # get night name whitelist
        _wnightnames = params['INPUTS']['WNIGHTNAMES']
        # deal with non-null value
        if not drs_text.null_text(_wnightnames, ['None', '', 'All']):
            params['WNIGHTNAMES'] = params['INPUTS'].listp('WNIGHTNAMES')
    # ----------------------------------------------------------------------
    # add pi name list
    if 'PI_NAMES' in params['INPUTS']:
        # get list of pi names
        _pinames = params['INPUTS']['PI_NAMES']
        # deal with non-null value
        if not drs_text.null_text(_pinames, ['None', '', 'All']):
            params['PI_NAMES'] = params['INPUTS'].listp('PI_NAMES')
    # ----------------------------------------------------------------------
    # deal with having a file specified
    params['FILENAME'] = None
    if 'FILENAME' in params['INPUTS']:
        # get filename arg
        _filename = params['INPUTS']['FILENAME']
        # deal with non-null value
        if not drs_text.null_text(_filename, ['None', '', 'All']):
            # if it is a string treat it as a list of string (just a string
            #   works too)
            if isinstance(params['INPUTS']['FILENAME'], str):
                params['FILENAME'] = params['INPUTS'].listp('FILENAME')
            # should really get here but set it to the _filename value anyway
            else:
                params['FILENAME'] = _filename
    # ----------------------------------------------------------------------
    # deal with getting test run from user input
    if 'TEST' in params['INPUTS']:
        # get the value of test
        _test = params['INPUTS']['TEST']
        # deal with non null value
        if not drs_text.null_text(_test, ['', 'None']):
            # test for true value
            params['TEST_RUN'] = drs_text.true_text(_test)
    # ----------------------------------------------------------------------
    # deal with getting trigger run from user input
    if 'TRIGGER' in params['INPUTS']:
        # get the value of trigger
        _trigger = params['INPUTS']['TRIGGER']
        # deal with non null values
        if not drs_text.null_text(_trigger, ['', 'None']):
            # test for true value
            params['TRIGGER_RUN'] = drs_text.true_text(_trigger)

        # if trigger if defined night name must be as well
        if params['NIGHTNAME'] is None and params['TRIGGER_RUN']:
            # cause an error if nightname not set
            WLOG(params, 'error', TextEntry('09-503-00010'))
    # ----------------------------------------------------------------------
    # relock params
    params.lock()
    # ----------------------------------------------------------------------
    # return parameter dictionary and runtable
    return params, runtable


def generate_skip_table(params):
    """
    Uses the log.fits files to generate a list of previous run recipes
    skips will occur when arguments are identical

    :param params:
    :return:
    """
    # log process
    WLOG(params, '', TextEntry('90-503-00017'))
    # get parameters from params
    logfitsfile = params['DRS_LOG_FITS_NAME']
    tmpdir = params['DRS_DATA_WORKING']
    reddir = params['DRS_DATA_REDUC']

    # storage log files
    logfiles = []
    # search tmp path for log files
    for root, dirs, files in os.walk(tmpdir):
        for filename in files:
            if filename == logfitsfile:
                logfiles.append(os.path.join(root, filename))
    # search reduced path for log files
    for root, dirs, files in os.walk(reddir):
        for filename in files:
            if filename == logfitsfile:
                logfiles.append(os.path.join(root, filename))

    # sort log files by name and only keep unique ones (shouldn't happen)
    logfiles = np.unique(logfiles)
    logfiles = np.sort(logfiles)
    # storage for recipe args
    recipes, arguments = [], []
    # loop around log files and
    for logfile in logfiles:
        # load table
        try:
            # load log table
            logtable = Table.read(logfile, format='fits')
            # debug printout
            dargs = [len(logtable), logfile]
            WLOG(params, 'debug', TextEntry('90-503-00019', args=dargs))
            # only keep those that finished
            ended = logtable['ENDED']
            logtable = logtable[ended]
            # log debug: number that ended
            dargs = [len(logtable)]
            WLOG(params, 'debug', TextEntry('90-503-00020', args=dargs))
            # append to storage
            recipes += list(logtable['RECIPE'])
            # get run string
            runstrings = list(logtable['RUNSTRING'])
            # loop around runstrings
            for runstring in runstrings:
                # clean run string
                clean_runstring = skip_clean_arguments(runstring)
                # append only clean arguments
                arguments.append(clean_runstring)
        except:
            continue

    # deal with nothing to skip
    if len(recipes) == 0:
        return None
    # push into skip table
    skip_table = Table()
    skip_table['RECIPE'] = recipes
    skip_table['RUNSTRING'] = arguments
    # log number of runs found
    WLOG(params, '', TextEntry('90-503-00018', args=[len(skip_table)]))
    # return skip table
    return skip_table


def skip_clean_arguments(runstring):
    """
    Clean arguments for skip check - these are arguments that may change
    between otherwise identical runs

    i.e. --prog depends on what is run
         --plot and --debug do not change run
         --skip should not determine same run

    :param runstring:
    :return:
    """
    args = np.array(runstring.split(' '))
    # mask for arguments to keep
    mask = np.ones(len(args)).astype(bool)
    # loop around arguments and figure out whether to keep them
    for it, arg in enumerate(args):
        for remove_arg in SKIP_REMOVE_ARGS:
            if arg.startswith(remove_arg):
                mask[it] = False
    return ' '.join(args[mask])


def skip_remove_non_required_args(runstrings, runobj):
    """
    remove any non-required arguments from runstrings (for skip comparison)

    :param runstrings:
    :param runobj:
    :return:
    """
    # get list of required args
    reqargs = runobj.required_args
    # deasl with runstrings as a string
    if isinstance(runstrings, str):
        runstrings = [runstrings]
    # new runstrings
    new_runstrings = []
    # loop around run strings
    for runstring in runstrings:
        # make prev_arg a list
        args = np.array(runstring.split(' '))
        # mask for arguments to keep
        mask = np.ones(len(args)).astype(bool)
        # set keep to False
        keep = True
        # loop around arguments and figure out whether to keep them
        for it, arg in enumerate(args):
            # only deal with optional arguments
            if arg.startswith('--'):
                keep = False
                # loop around keep arguments
                for keep_arg in reqargs:
                    if arg.startswith('--{0}'.format(keep_arg)):
                        keep = True
            mask[it] = keep
        # append to new_runstrings
        new_runstrings.append(' '.join(args[mask]))
    # return new runstrings
    return np.unique(new_runstrings)



def fix_run_file(runfile):
    # only do this if we have a runfile
    if os.path.exists(runfile):
        # read the lines
        with open(runfile, 'r') as f:
            lines = f.readlines()

        # convert to character array
        lines = np.char.array(lines)
        # replace all equal signs
        lines = lines.replace('=', '@' * 50, 1)
        lines = lines.replace('=', ' ')
        lines = lines.replace('@' * 50, '=')
        # write to file
        with open(runfile, 'w') as f:
            # write lines to file
            for line in lines:
                f.write(line + '\n')


def send_email(params, kind):
    func_name = __NAME__ + '.send_email()'
    # ----------------------------------------------------------------------
    # get text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # ----------------------------------------------------------------------
    # check whether send email
    if not params['SEND_EMAIL']:
        return 0
    # ----------------------------------------------------------------------
    # try to import yagmail
    try:
        import yagmail
        yag = yagmail.SMTP(params['EMAIL_ADDRESS'])
    except ImportError:
        WLOG(params, 'error', TextEntry('00-503-00001'))
        yagmail = None
        yag = yagmail
    except Exception as e:
        eargs = [type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-503-00002', args=eargs))
        yagmail = None
        yag = yagmail
    # ----------------------------------------------------------------------
    # deal with kind = start
    if kind == 'start':
        receiver = params['EMAIL_ADDRESS']
        iname = '{0}-DRS'.format(params['INSTRUMENT'])
        sargs = [iname, __NAME__, params['PID']]
        subject = textdict['40-503-00001'].format(*sargs)
        body = ''
        for logmsg in WLOG.pout['LOGGER_ALL']:
            body += '{0}\t{1}\n'.format(*logmsg)
    # ----------------------------------------------------------------------
    # deal with kind = end
    elif kind == 'end':
        receiver = params['EMAIL_ADDRESS']
        iname = '{0}-DRS'.format(params['INSTRUMENT'])
        sargs = [iname, __NAME__, params['PID']]
        subject = textdict['40-503-00002'].format(*sargs)
        body = ''
        for logmsg in params['LOGGER_FULL']:
            for log in logmsg:
                body += '{0}\t{1}\n'.format(*log)
    # ----------------------------------------------------------------------
    # else do not send email
    else:
        return 0
    # ----------------------------------------------------------------------
    # send via YAG
    yag.send(to=receiver, subject=subject, contents=body)


def reset_files(params):
    """
    Resets based on reset parameters

    :param params: ParamDict, the parameter dictionary

    :type params: ParamDict

    :returns: None
    """
    if not params['RESET_ALLOWED']:
        return 0
    if params['RESET_TMP']:
        reset = drs_reset.reset_confirmation(params, 'Working',
                                             params['DRS_DATA_WORKING'])
        if reset:
            drs_reset.reset_tmp_folders(params, log=True)
    if params['RESET_REDUCED']:
        reset = drs_reset.reset_confirmation(params, 'Reduced',
                                             params['DRS_DATA_REDUC'])
        if reset:
            drs_reset.reset_reduced_folders(params, log=True)
    if params['RESET_CALIB']:
        reset = drs_reset.reset_confirmation(params, 'Calibration',
                                             params['DRS_CALIB_DB'])
        if reset:
            drs_reset.reset_calibdb(params, log=True)
    if params['RESET_TELLU']:
        reset = drs_reset.reset_confirmation(params, 'Telluric',
                                             params['DRS_TELLU_DB'])
        if reset:
            drs_reset.reset_telludb(params, log=True)
    if params['RESET_LOG']:
        reset = drs_reset.reset_confirmation(params, 'Log',
                                             params['DRS_DATA_MSG'])
        if reset:
            drs_reset.reset_log(params)
    if params['RESET_PLOT']:
        reset = drs_reset.reset_confirmation(params, 'Plotting',
                                             params['DRS_DATA_PLOT'])
        if reset:
            drs_reset.reset_plot(params)
    if params['RESET_RUN']:
        reset = drs_reset.reset_confirmation(params, 'Run',
                                             params['DRS_DATA_RUN'])
        if reset:
            drs_reset.reset_run(params)
    if params['RESET_LOGFITS']:
        reset = drs_reset.reset_confirmation(params, 'log_fits')
        if reset:
            drs_reset.reset_log_fits(params)


def generate_run_list(params, table, runtable, skiptable):
    # print progress: generating run list
    WLOG(params, 'info', TextEntry('40-503-00011'))
    # need to update table object names to match preprocessing
    #   table can be None if coming from e.g fit_tellu_db
    if table is not None:
        table = _update_table_objnames(params, table)
    # get recipe defintions module (for this instrument)
    recipemod = _get_recipe_module(params)
    # get all values (upper case) using map function
    rvalues = _get_rvalues(runtable)
    # check if rvalues has a run sequence
    sequencelist = _check_for_sequences(rvalues, recipemod)
    # set rlist to None (for no sequences)
    rlist = None
    # if we have found sequences need to deal with them
    #   also table cannot be None at this point
    if (sequencelist is not None) and (table is not None):
        # loop around sequences
        for sequence in sequencelist:
            # log progress
            WLOG(params, '', TextEntry('40-503-00009', args=[sequence[0]]))
            # generate new runs for sequence
            newruns = _generate_run_from_sequence(params, sequence, table)
            # update runtable with sequence generation
            runtable, rlist = update_run_table(sequence, runtable, newruns,
                                               rlist)
    # all runtable elements should now be in recipe list
    _check_runtable(params, runtable, recipemod)
    # return Run instances for each runtable element
    return generate_ids(params, runtable, recipemod, skiptable, rlist)


def process_run_list(params, recipe, runlist, group=None):
    # get number of cores
    cores = _get_cores(params)
    # pipe to correct module
    if cores == 1:
        # log process: Running with 1 core
        WLOG(params, 'info', TextEntry('40-503-00016'))
        # run as linear process
        rdict = _linear_process(params, recipe, runlist, group=group)
    else:
        # log process: Running with N cores
        WLOG(params, 'info', TextEntry('40-503-00017', args=[cores]))
        # run as multiple processes
        rdict = _multi_process(params, recipe, runlist, cores=cores,
                               groupname=group)

    # remove lock files
    drs_lock.reset_lock_dir(params)

    # convert to dict
    odict = OrderedDict()
    keys = np.sort(np.array(list(rdict.keys())))
    for key in keys:
        odict[key] = dict(rdict[key])

    # see if we have any errors
    errors = False
    for key in keys:
        if len(odict[key]['ERROR']) != 0:
            errors = True

    # return the output array (dictionary with priority as key)
    #    values is a parameter dictionary consisting of
    #        RECIPE, NIGHT_NAME, ARGS, ERROR, WARNING, OUTPUTS
    return odict, errors


def display_timing(params, outlist):
    WLOG(params, '', '')
    WLOG(params, '', params['DRS_HEADER'])
    WLOG(params, '', 'Timings:')
    WLOG(params, '', params['DRS_HEADER'])
    WLOG(params, '', '')
    # sort outlist ids
    keys = np.sort(list(outlist.keys()))
    # store times
    tot_time = 0
    # loop around timings (non-errors only)
    for key in keys:
        cond1 = len(outlist[key]['ERROR']) == 0
        cond2 = outlist[key]['TIMING'] is not None
        if cond1 and cond2:
            wargs = [key, outlist[key]['TIMING']]
            WLOG(params, '', TextEntry('40-503-00020', args=wargs))
            WLOG(params, '', '\t\t{0}'.format(outlist[key]['RUNSTRING']),
                 wrap=False)
            WLOG(params, '', '')
            # add to total time
            tot_time += outlist[key]['TIMING']
    # add total time
    WLOG(params, '', params['DRS_HEADER'])
    WLOG(params, 'info', TextEntry('40-503-00025', args=[tot_time]))
    WLOG(params, '', params['DRS_HEADER'])
    WLOG(params, '', '')


def display_errors(params, outlist):
    # log error title
    WLOG(params, '', '')
    WLOG(params, '', params['DRS_HEADER'])
    WLOG(params, '', 'Errors:')
    WLOG(params, '', params['DRS_HEADER'])
    WLOG(params, '', '')
    # sort outlist ids
    keys = np.sort(list(outlist.keys()))
    # loop around each entry of outlist and print any errors
    for key in keys:
        if len(outlist[key]['ERROR']) > 0:
            WLOG(params, '', '', colour='red')
            WLOG(params, '', params['DRS_HEADER'], colour='red')
            WLOG(params, 'warning', TextEntry('40-503-00019', args=[key]),
                 colour='red', wrap=False)
            WLOG(params, 'warning', '\t{0}'.format(outlist[key]['RUNSTRING']),
                 colour='red', wrap=False)
            WLOG(params, '', params['DRS_HEADER'], colour='red')
            WLOG(params, '', '', colour='red')
            # --------------------------------------------------------------
            # deal with list from out error
            for error in outlist[key]['ERROR']:
                if isinstance(error, list):
                    strerror = '{1}'.format(*error)
                else:
                    strerror = str(error)
                WLOG.printmessage(params, strerror, colour='red')
                WLOG.logmessage(params, strerror)
            WLOG(params, '', '', colour='red')
            # --------------------------------------------------------------
            # deal with list from out traceback
            if isinstance(outlist[key]['TRACEBACK'], str):
                tbacklist = [outlist[key]['TRACEBACK']]
            else:
                tbacklist = outlist[key]['TRACEBACK']
            # loop around trace back list
            for tback in tbacklist:
                if isinstance(tback, list):
                    strtback = '{1}'.format(*tback)
                else:
                    strtback = str(tback)
                WLOG.printmessage(params, strtback, colour='red')
                WLOG.logmessage(params, strtback)
            WLOG(params, '', '', colour='red')
            # --------------------------------------------------------------
            WLOG(params, '', params['DRS_HEADER'], colour='red')
    WLOG(params, '', '')


def save_stats(params, outlist):
    # set function name
    func_name = __NAME__ + '.save_stats()'
    # get save directory
    save_dir = os.path.join(params['DRS_DATA_RUN'], 'stats')
    # deal with stats dir not existing
    if not os.path.exists(save_dir):
        try:
            os.mkdir(save_dir)
        except Exception as e:
            eargs = [save_dir, type(e), e, func_name]
            WLOG(params, 'warning', TextEntry('10-503-00011', args=eargs))
            return
    # get log file name
    log_abs_file = drs_log.get_logfilepath(WLOG, params)
    log_file = os.path.basename(log_abs_file)
    # get fits file out path
    out_fitsfile = log_file.replace('.log', '_stats.fits')
    out_fits_path = os.path.join(save_dir, out_fitsfile)
    # get txt file out path
    out_txtfile = log_file.replace('.log', '_stats.txt')
    out_txt_path = os.path.join(save_dir, out_txtfile)
    # define storage
    priorities = []
    runlists = []
    recipenames = []
    nightnames = []
    coresused = []
    corestot = []
    groups = []
    # sort outlist ids
    keys = np.sort(list(outlist.keys()))
    # loop around each entry of outlist and print any errors
    for key in keys:
        # get rdict
        rdict = outlist[key]
        # append priorities
        priorities.append(key)
        # append runstring to run lists
        runlists.append(rdict['RUNSTRING'])
        # append recipes to list
        recipenames.append(rdict['RECIPE'])
        # append night name to list
        nightnames.append(rdict['NIGHTNAME'])
        # append cores used to list
        coresused.append(rdict['COREUSED'])
        # append cores total
        corestot.append(rdict['CORETOT'])
        # append group
        groups.append(rdict['GROUP'])
    # make into a table
    columns = ['ID', 'RECIPE', 'NIGHT', 'CORE_NUM', 'CORE_TOT', 'RUNSTRING']
    values = [priorities, recipenames, nightnames, coresused, corestot,
              runlists]
    out_fits_table = drs_table.make_table(params, columns, values)
    # write table
    try:
        drs_table.write_table(params, out_fits_table, out_fits_path)
    except Exception as e:
        eargs = [out_fits_path, type(e), e, func_name]
        WLOG(params, 'warning', TextEntry('10-503-00012', args=eargs))

    # make txt table
    try:
        with open(out_txt_path, 'w') as f:
            for value in runlists:
                f.write(value + '\n')
    except Exception as e:
        eargs = [out_txt_path, type(e), e, func_name]
        WLOG(params, 'warning', TextEntry('10-503-00012', args=eargs))


def generate_run_table(params, recipe, *args, **kwargs):
    func_name = __NAME__ + '.generate_run_table()'
    # set length initially to None
    length = None
    # loop around arguments and identify list of arguments
    for it, arg in enumerate(args):
        # if we have a list it needs to be the same length as all other list
        # arguments
        if isinstance(arg, list):
            if length is None:
                length = len(arg)
            elif len(arg) != length:
                eargs = ['Arg {0}'.format(it), length, func_name]
                WLOG(params, 'error', TextEntry('00-503-00010', args=eargs))
    # loop around keyword arguments and identify list of arguments
    for kwarg in kwargs:
        # if we have a list it needs to be the same length as all other list
        # arguments
        if isinstance(kwargs[kwarg], list):
            if length is None:
                length = len(kwargs[kwarg])
            elif len(kwargs[kwarg]) != length:
                # log error we need all lists to have the same number of
                #    elements
                eargs = [kwarg, length, func_name]
                WLOG(params, 'error', TextEntry('00-503-00010', args=eargs))
    # length could still be None should be 1
    if length is None:
        length = 1
    # now we have checked arguments can generate runs
    run_table = OrderedDict()
    # loop around rows up to length
    for row in range(length):
        # get base command
        command = '{0}'.format(recipe.name)
        # loop around args
        for arg in args:
            if isinstance(arg, list):
                command += ' {0}'.format(arg[row])
            else:
                command += ' {0}'.format(arg)
        # loop around kwargs
        for kwarg in kwargs:
            if isinstance(kwargs[kwarg], list):
                command += ' {0}={1}'.format(kwarg, kwargs[kwarg][row])
            else:
                command += ' {0}={1}'.format(kwarg, kwargs[kwarg])
        # add to run table
        run_table[row] = command
    # return run table
    return run_table


# =============================================================================
# Define "from id" functions
# =============================================================================
def generate_ids(params, runtable, mod, skiptable, rlist=None, **kwargs):
    func_name = __NAME__ + '.generate_ids()'
    # get keys from params
    run_key = pcheck(params, 'REPROCESS_RUN_KEY', 'run_key', kwargs, func_name)
    # should just need to sort these
    numbers = np.array(list(runtable.keys()))
    commands = np.array(list(runtable.values()))
    # create text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # deal with unset rlist (recipe list)
    if rlist is not None:
        inrecipes = np.array(list(rlist.values()))
    else:
        inrecipes = np.array([None] * len(numbers))
    # sort by number
    sortmask = np.argsort(numbers)
    # get sorted run list
    runlist = list(commands[sortmask])
    keylist = list(numbers[sortmask])
    inrecipelist = list(inrecipes[sortmask])
    # store skip previous runstrings (so it is not recalculated every time)
    skip_storage = dict()
    # log progress: Validating ids
    WLOG(params, 'info', TextEntry('40-503-00015', args=[len(runlist)]))
    # iterate through and make run objects
    run_objects = []
    for it, run_item in enumerate(runlist):
        # get runid
        runid = '{0}{1:05d}'.format(run_key, keylist[it])
        # get recipe
        input_recipe = inrecipelist[it]
        # log process: validating run
        wargs = [runid, it + 1, len(runlist)]
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', TextEntry('40-503-00004', args=wargs))
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', TextEntry('40-503-00013', args=[run_item]))
        # create run object
        run_object = Run(params, run_item, mod=mod, priority=keylist[it],
                         inrecipe=input_recipe)
        # deal with input recipe
        if input_recipe is None:
            input_recipe = run_object.recipe
        # deal with skip
        skip, reason = skip_run_object(params, run_object, skiptable, textdict,
                                       skip_storage)
        # deal with passing debug
        if params['DRS_DEBUG'] > 0:
            dargs = [run_object.runstring, params['DRS_DEBUG']]
            run_object.runstring = '{0} --debug={1}'.format(*dargs)
            run_object.update()
        # deal with passing master argument
        if input_recipe.master:
            dargs = [run_object.runstring, 'True']
            run_object.runstring = '{0} --master={1}'.format(*dargs)
            run_object.update()
        # append to list
        if not skip:
            # log that we have validated run
            wargs = [runid]
            WLOG(params, '', TextEntry('40-503-00005', args=wargs))
            # append to run_objects
            run_objects.append(run_object)
        # else log that we are skipping
        else:
            # log that we have skipped run
            wargs = [runid, reason]
            WLOG(params, '', TextEntry('40-503-00006', args=wargs),
                 colour='yellow')
    # return run objects
    return run_objects


def skip_run_object(params, runobj, skiptable, textdict, skip_storage):
    # get recipe and runstring
    recipe = runobj.recipe
    # ----------------------------------------------------------------------
    # check if the user wants to run this runobj (in run list)
    if runobj.runname in params:
        # if user has set the runname to False then we want to skip
        if not params[runobj.runname]:
            return True, textdict['40-503-00007']
    # ----------------------------------------------------------------------
    # deal with skip table being empty
    if skiptable is None:
        return False, None
    # ----------------------------------------------------------------------
    # check if the user wants to skip
    if runobj.skipname in params:
        # if user wants to skip
        if params[runobj.skipname]:
            # clean run string
            clean_runstring = skip_clean_arguments(runobj.runstring)
            # check for recipe in skip storage
            if recipe.name.strip('.py') in skip_storage:
                # get the cleaned arguments directory from skip_storage
                #   (quicker than re-calculating)
                arguments = skip_storage[recipe.name.strip('.py')]
            else:
                # mask skip table by recipe
                mask = skiptable['RECIPE'] == recipe.name.strip('.py')
                # get valid arguments to check
                arguments = skiptable['RUNSTRING'][mask]
                # re-clean arguments this time using additional recipe
                #    requirements
                arguments = skip_remove_non_required_args(arguments, runobj)
                # update skip storage (so we don't do this again)
                skip_storage[recipe.name.strip('.py')] = arguments
            # if the clean run string is in the arguments list then we skip
            # TODO: problem with clean_runstring being a list??
            if clean_runstring in arguments:
                # User set skip to 'True' and argument previously used
                return True, textdict['40-503-00032']
            else:
                return False, None
        else:
            # debug log
            dargs = [runobj.skipname]
            WLOG(params, 'debug', TextEntry('90-503-00004', args=dargs))
            # return False and no reason
            return False, None
    # ----------------------------------------------------------------------
    else:
        # debug log
        dargs = [runobj.skipname]
        WLOG(params, '', TextEntry('90-503-00005', args=dargs))
        # return False and no reason
        return False, '{0} not present'.format(runobj.skipname)


# TODO: remove later
def skip_run_object_old(params, runobj):
    # create text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # get recipe and runstring
    recipe = runobj.recipe
    runstring = runobj.runstring

    # debug log giving info on name/runname/skipname
    dargs = [recipe.name, recipe.shortname, runobj.runname, runobj.skipname]
    WLOG(params, 'debug', TextEntry('90-503-00010', args=dargs))
    # ----------------------------------------------------------------------
    # check if the user wants to run this runobj (in run list)
    if runobj.runname in params:
        # if user has set the runname to False then we want to skip
        if not params[runobj.runname]:
            return True, textdict['40-503-00007']
    # ----------------------------------------------------------------------
    # check if the user wants to skip
    if runobj.skipname in params:
        # if master in skipname do not skip
        if runobj.master:
            # debug log
            dargs = [runobj.skipname]
            WLOG(params, 'debug', TextEntry('90-503-00003', args=dargs))
            # return False and no reason
            return False, None
        # else if user wants to skip
        elif params[runobj.skipname]:
            # deal with adding skip to recipes
            if 'skip' in recipe.kwargs:
                if '--skip' in runstring:
                    # debug log
                    WLOG(params, 'debug', TextEntry('90-503-00007'))
                    return False, None

            # look for fits files in args
            return _check_for_files(params, runobj)
        else:
            # debug log
            dargs = [runobj.skipname]
            WLOG(params, 'debug', TextEntry('90-503-00004', args=dargs))
            # return False and no reason
            return False, None
    # ----------------------------------------------------------------------
    else:
        # debug log
        dargs = [runobj.skipname]
        WLOG(params, 'debug', TextEntry('90-503-00005', args=dargs))
        # return False and no reason
        return False, None


def _get_paths(params, runobj, directory):
    func_name = __NAME__ + '.get_paths()'

    recipe = runobj.recipe
    # ----------------------------------------------------------------------
    # get the night name from directory position
    nightname = runobj.args[int(directory.pos) + 1]
    # ----------------------------------------------------------------------
    # get the input directory
    if recipe.inputdir == 'raw':
        inpath = os.path.join(params['DRS_DATA_RAW'], nightname)
    elif recipe.inputdir == 'tmp':
        inpath = os.path.join(params['DRS_DATA_WORKING'], nightname)
    elif recipe.inputdir.startswith('red'):
        inpath = os.path.join(params['DRS_DATA_REDUC'], nightname)
    else:
        eargs = [recipe.name, recipe.outputdir, func_name]
        WLOG(params, 'error', TextEntry('09-503-00007', args=eargs))
        inpath = None
    # ----------------------------------------------------------------------
    # check that path exist
    if not os.path.exists(inpath):
        try:
            os.makedirs(inpath)
        except Exception as e:
            eargs = [recipe.name, runobj.runstring, inpath, type(e), e,
                     func_name]
            WLOG(params, 'error', TextEntry('09-503-00008', args=eargs))
    # ----------------------------------------------------------------------
    # get the output directory
    if recipe.outputdir == 'raw':
        outpath = os.path.join(params['DRS_DATA_RAW'], nightname)
    elif recipe.outputdir == 'tmp':
        outpath = os.path.join(params['DRS_DATA_WORKING'], nightname)
    elif recipe.outputdir.startswith('red'):
        outpath = os.path.join(params['DRS_DATA_REDUC'], nightname)
    else:
        eargs = [recipe.name, recipe.outputdir, func_name]
        WLOG(params, 'error', TextEntry('09-503-00005', args=eargs))
        outpath = None
    # ----------------------------------------------------------------------
    # check that path exist
    if not os.path.exists(outpath):
        try:
            os.makedirs(outpath)
        except Exception as e:
            eargs = [recipe.name, runobj.runstring, outpath, type(e), e,
                     func_name]
            WLOG(params, 'error', TextEntry('09-503-00006', args=eargs))
    # ----------------------------------------------------------------------
    # return inpath and outpath
    return inpath, outpath, nightname


# TODO: no longer used?
def _check_for_files(params, runobj):
    # create text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # get fits files from args
    files = []
    for arg in runobj.args:
        if arg.endswith('.fits'):
            files.append(arg)
    # set recipe
    recipe = runobj.recipe
    # get args and keyword args for recipe
    args, kwargs = recipe.args, recipe.kwargs
    # ----------------------------------------------------------------------
    # if we don't have a directory argument we skip this test
    if 'directory' not in args and 'directory' not in kwargs:
        WLOG(params, 'debug', TextEntry('90-503-00002'))
        return False, None
    elif 'directory' in args:
        directory = args['directory']
    else:
        directory = kwargs['directory']
    # ----------------------------------------------------------------------
    # get input and output paths
    inpath, outpath, nightname = _get_paths(params, runobj, directory)
    # ----------------------------------------------------------------------
    # store outfiles (for debug)
    outfiles = []
    # ----------------------------------------------------------------------
    # get in files
    infiles = []
    # loop around file names
    for filename in files:
        # ------------------------------------------------------------------
        # make sure filename is a base filename
        basename = os.path.basename(filename)
        # make infile
        if runobj.kind == 0:
            infiledef = recipe.filemod.get().raw_file
        elif runobj.kind == 1:
            infiledef = recipe.filemod.get().pp_file
        else:
            infiledef = recipe.filemod.get().out_file
        # ------------------------------------------------------------------
        # add required properties to infile
        infile = infiledef.newcopy(params=params)
        infile.filename = os.path.join(inpath, filename)
        infile.basename = basename
        # append to infiles
        infiles.append(infile)

    # ----------------------------------------------------------------------
    # for each file see if we have a file that exists
    #   (if we do we skip and assume this recipe was completed)
    for infile in infiles:
        # ------------------------------------------------------------------
        # loop around output files
        for outputkey in recipe.outputs:
            # get output
            output = recipe.outputs[outputkey]
            # add the infile type from output
            if output.intype is None:
                continue
            elif isinstance(output.intype, list):
                infile.filetype = output.intype[0].filetype
            else:
                infile.filetype = output.intype.filetype
            # define outfile
            outfile = output.newcopy(params=params)
            # --------------------------------------------------------------
            # check whether we need to add fibers
            if output.fibers is not None:
                # loop around fibers
                for fiber in output.fibers:
                    # construct file name
                    outfile.construct_filename(infile=infile,
                                               fiber=fiber, path=outpath,
                                               nightname=nightname, check=False)
                    # get outfilename absolute path
                    outfilename = outfile.filename
                    # if file is found return True
                    if os.path.exists(outfilename):
                        reason = textdict['40-503-00008'].format(outfilename)
                        return True, reason
                    else:
                        outfiles.append(outfilename)
            else:
                # construct file name
                outfile.construct_filename(infile=infile, path=outpath,
                                           nightname=nightname, check=False)
                # get outfilename absolute path
                outfilename = outfile.filename
                # if file is found return True
                if os.path.exists(outfilename):
                    reason = textdict['40-503-00008'].format(outfilename)
                    return True, reason
                else:
                    outfiles.append(outfilename)
    # ----------------------------------------------------------------------
    # debug print
    for outfile in outfiles:
        WLOG(params, 'debug', TextEntry('90-503-00001', args=[outfile]))
    # ----------------------------------------------------------------------
    # if all tests are passed return False
    return False, None


def _remove_py(innames):
    if isinstance(innames, str):
        names = [innames]
    else:
        names = innames
    outnames = []
    for name in names:
        while name.endswith('.py'):
            name = name[:-3]
        outnames.append(name)
    if isinstance(innames, str):
        return outnames[0]
    else:
        return outnames


# =============================================================================
# Define "from sequence" functions
# =============================================================================
def _check_for_sequences(rvalues, mod):
    # find sequences
    all_sequences = mod.get().sequences
    # get sequences names
    all_seqnames = list(map(lambda x: x.name, all_sequences))
    # convert to uppercase
    all_seqnames = list(map(lambda x: x.upper(), all_seqnames))
    # storage for found sequences
    sequencelist = []
    # loop around rvalues and add to sequence
    for rvalue in rvalues:
        if rvalue in all_seqnames:
            # find position of name
            pos = all_seqnames.index(rvalue)
            # append sequences
            sequencelist.append([rvalue, all_sequences[pos]])
    # deal with return of sequences (found/not found)
    if len(sequencelist) == 0:
        return None
    else:
        return sequencelist


def _generate_run_from_sequence(params, sequence, table, **kwargs):
    func_name = __NAME__ + '.generate_run_from_sequence()'
    # get parameters from params/kwargs
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
    piname_col = pcheck(params, 'REPROCESS_PINAMECOL', 'piname_col', kwargs,
                        func_name)
    # get all telluric stars
    tstars = telluric.get_whitelist(params)
    # get all other stars
    ostars = _get_non_telluric_stars(params, table, tstars)
    # get filemod and recipe mod
    pconst = constants.pload(params['INSTRUMENT'])
    filemod = pconst.FILEMOD()
    recipemod = pconst.RECIPEMOD()
    # generate sequence
    sequence[1].process_adds(params, tstars=list(tstars), ostars=list(ostars))
    # get the sequence recipe list
    srecipelist = sequence[1].sequence
    # storage for new runs to add
    newruns = []
    # loop around recipes in new list
    for srecipe in srecipelist:
        # deal with skip
        runname = 'RUN_{0}'.format(srecipe.shortname)
        # skip if runname is not True
        if runname in params:
            if not params[runname]:
                wargs = [srecipe.name, srecipe.shortname]
                WLOG(params, '', TextEntry('40-503-00021', args=wargs),
                     colour='yellow')
                continue
        # print progress
        wargs = [srecipe.name, srecipe.shortname]
        WLOG(params, '', TextEntry('40-503-00012', args=wargs))
        # add file and recipe mod if not set
        if srecipe.recipemod is None:
            srecipe.recipemod = recipemod.copy()
        if srecipe.filemod is None:
            srecipe.filemod = filemod.copy()
        # add params to srecipe
        srecipe.params = params
        # ------------------------------------------------------------------
        # copy table
        # ------------------------------------------------------------------
        ftable = Table(table)
        # skip if table is empty
        if len(ftable) == 0:
            continue

        # ------------------------------------------------------------------
        # deal with black and white lists
        # ------------------------------------------------------------------


        # ------------------------------------------------------------------
        # deal with black and white lists
        # ------------------------------------------------------------------
        # black list
        if not drs_text.null_text(params['BNIGHTNAMES'], ['', 'All', 'None']):
            # start by assuming we want to keep everything
            mask = np.ones(len(ftable), dtype=bool)
            # get black list from params
            blacklist_nights = params.listp('BNIGHTNAMES', dtype=str)
            # loop around black listed nights and set them to False
            for blacklist_night in blacklist_nights:
                mask &= (ftable[night_col] != blacklist_night)
            # apply mask to table
            ftable = ftable[mask]
            # log blacklist
            wargs = [' ,'.join(blacklist_nights)]
            WLOG(params, '', TextEntry('40-503-00026', args=wargs))

            # deal with empty ftable
            if len(ftable) == 0:
                WLOG(params, 'warning', TextEntry('10-503-00006'))
                # get response for how to continue (skip or exit)
                response = prompt(params)
                if response:
                    continue
                else:
                    sys.exit()
        # ------------------------------------------------------------------
        # white list
        if not drs_text.null_text(params['WNIGHTNAMES'], ['', 'All', 'None']):
            # start by assuming we want to keep nothing
            mask = np.zeros(len(ftable), dtype=bool)
            # get white list from params
            whitelist_nights = params.listp('WNIGHTNAMES', dtype=str)
            # loop around white listed nights and set them to False
            for whitelist_night in whitelist_nights:
                mask |= (ftable[night_col] == whitelist_night)
            # apply mask to table
            ftable = ftable[mask]
            # log blacklist
            wargs = [' ,'.join(whitelist_nights)]
            WLOG(params, '', TextEntry('40-503-00027', args=wargs))
            # deal with empty ftable
            if len(ftable) == 0:
                WLOG(params, 'warning', TextEntry('10-503-00007'))
                # get response for how to continue (skip or exit)
                response = prompt(params)
                if response:
                    continue
                else:
                    sys.exit()
        # ------------------------------------------------------------------
        # pi name list
        if not drs_text.null_text(params['PI_NAMES'], ['', 'All', 'None']):
            # start by assuming we want to keep nothing
            mask = np.zeros(len(ftable), dtype=bool)
            # get pi name list from params
            pi_names = params.listp('PI_NAMES', dtype=str)
            # loop around pi names and set them to False
            for pi_name in pi_names:
                mask |= (ftable[piname_col] == pi_name)
            # apply mask to table
            ftable = ftable[mask]
            # log blacklist
            wargs = [' ,'.join(pi_names)]
            WLOG(params, '', TextEntry('40-503-00029', args=wargs))
            # deal with empty ftable
            if len(ftable) == 0:
                WLOG(params, 'warning', TextEntry('10-503-00015'))
                # get response for how to continue (skip or exit)
                response = prompt(params)
                if response:
                    continue
                else:
                    sys.exit()

        # ------------------------------------------------------------------
        # deal with a night name
        # ------------------------------------------------------------------
        # deal with nightname
        if srecipe.master:
            nightname = params['MASTER_NIGHT']
            # check if master night name is valid (in table)
            if nightname not in ftable[night_col]:
                wargs = [nightname]
                WLOG(params, 'warning', TextEntry('10-503-00004', args=wargs))
                # get response for how to continue (skip or exit)
                response = prompt(params)
                if response:
                    continue
                else:
                    sys.exit()
            # mask table by nightname
            mask = ftable[night_col] == nightname
            ftable = Table(ftable[mask])

        if not drs_text.null_text(params['NIGHTNAME'], ['', 'All', 'None']):
            nightname = params['NIGHTNAME']
            # mask table by nightname
            mask = ftable[night_col] == nightname
            ftable = ftable[mask]
        else:
            nightname = 'all'
        # ------------------------------------------------------------------
        # deal with empty ftable
        if len(ftable) == 0:
            wargs = [nightname]
            WLOG(params, 'warning', TextEntry('10-503-00003', args=wargs))
            # get response for how to continue (skip or exit)
            response = prompt(params)
            if response:
                continue
            else:
                sys.exit()
        # filer out engineering
        if not params['ENGINEERING']:
            ftable = _remove_engineering(params, ftable)
        # deal with filters
        filters = _get_filters(params, srecipe)

        # get fiber filter
        allowedfibers = srecipe.allowedfibers
        # get runs for this recipe
        sruns = srecipe.generate_runs(ftable, filters=filters,
                                      allowedfibers=allowedfibers)
        # ------------------------------------------------------------------
        # if we are in trigger mode we need to stop when we have no
        #   sruns for recipe
        if params['INPUTS']['TRIGGER'] and len(sruns) == 0:
            # display message that we stopped here as no files were found
            wargs = [srecipe.name]
            WLOG(params, 'info', TextEntry('40-503-00028', args=wargs))
            # stop processing recipes
            break

        # ------------------------------------------------------------------
        # append runs to new runs list
        for srun in sruns:
            newruns.append([srun, srecipe])
    # return all new runs
    return newruns


def update_run_table(sequence, runtable, newruns, rlist=None):
    # define output runtable
    outruntable = OrderedDict()
    recipe_list = OrderedDict()
    # new id number
    idnumber = 0
    # loop around runtable until we get to sequence
    for idkey in runtable:
        # if we have not found the id key
        if runtable[idkey].upper() != sequence[0]:
            # add run table row to out run table
            outruntable[idnumber] = runtable[idkey]
            if rlist is None:
                recipe_list[idnumber] = None
            else:
                recipe_list[idnumber] = rlist[idkey]
            # update id number
            idnumber += 1
        # else we have found where we need to insert rows
        else:
            for newrun in newruns:
                # add run table row to out run table
                outruntable[idnumber] = newrun[0]
                recipe_list[idnumber] = newrun[1]
                # update id number
                idnumber += 1
    # return out run table
    return outruntable, recipe_list


def prompt(params):
    # get the text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # prompt the user for response
    uinput = input(textdict['40-503-00022'])
    # get the True/False responses
    true = textdict['40-503-00023']
    false = textdict['40-503-00024']

    if true.upper() in uinput.upper():
        return 1
    elif false.upper() in uinput.upper():
        return 0
    else:
        return 1


# =============================================================================
# Define processing functions
# =============================================================================
def _linear_process(params, recipe, runlist, return_dict=None, number=0,
                    cores=1, event=None, group=None):
    # get textdict
    textdict = TextDict(params['instrument'], params['LANGUAGE'])
    # deal with empty return_dict
    if return_dict is None:
        return_dict = dict()
    # loop around runlist
    for run_item in runlist:
        # get parameters from params
        stop_at_exception = bool(params['STOP_AT_EXCEPTION'])
        # if master we should always stop at exception
        if run_item.master:
            stop_at_exception = True
        # ------------------------------------------------------------------
        # get the module
        modulemain = run_item.recipemod
        # get the kwargs
        kwargs = run_item.kwargs
        # get the priority
        priority = run_item.priority
        # parameters to save
        pp = dict()
        pp['RECIPE'] = str(run_item.recipename)
        pp['NIGHTNAME'] = str(run_item.nightname)
        pp['ARGS'] = kwargs
        pp['RUNSTRING'] = str(run_item.runstring)
        pp['COREUSED'] = number
        pp['CORETOT'] = cores
        pp['GROUP'] = group
        pp['STATE'] = 'None'
        # ------------------------------------------------------------------
        # add drs group to keyword arguments
        pp['ARGS']['DRS_GROUP'] = group
        # ------------------------------------------------------------------
        # log what we are running
        if cores > 1:
            wargs = [priority, number, cores, run_item.runstring]
            wmsg = 'ID{0:05d}|C{1:02d}/{2:02d}| {3}'.format(*wargs)
        else:
            wmsg = 'ID{0:05d}| {1}'.format(priority, run_item.runstring)
        # deal with a test run
        if params['TEST_RUN']:
            # log which core is being used
            WLOG(params, 'info', 'T' + wmsg, colour='magenta', wrap=False)
            # add default outputs
            pp['PID'] = None
            pp['ERROR'] = []
            pp['WARNING'] = []
            pp['OUTPUTS'] = dict()
            pp['TIMING'] = None
            pp['TRACEBACK'] = ''
            pp['SUCCESS'] = False
            pp['PASSED'] = False
            pp['STATE'] = 'TEST'
            # flag finished
            finished = True
        # --------------------------------------------------------------
        # deal with an event set -- skip
        # --------------------------------------------------------------
        elif event is not None and event.is_set():
            emsg = 'LINEAR PROCESS: Event set - skipping ID{0:05d}'
            WLOG(params, 'debug', emsg.format(priority))
            # deal with returns
            pp = dict()
            pp['PID'] = None
            pp['ERROR'] = []
            pp['WARNING'] = []
            pp['OUTPUTS'] = dict()
            pp['TRACEBACK'] = ''
            pp['SUCCESS'] = False
            pp['PASSED'] = False
            pp['STATE'] = 'SKIPPED:EVENT'
            finished = False
        # --------------------------------------------------------------
        # deal with an event set -- skip
        # --------------------------------------------------------------
        else:
            # --------------------------------------------------------------
            # log message
            WLOG(params, 'info', wmsg, colour='magenta', wrap=False)
            # --------------------------------------------------------------
            # do a final test that files exist
            passed = run_item.prerun_test()
            # --------------------------------------------------------------
            # deal with pre run test failing (file(s) not found)
            if not passed:
                # deal with returns
                pp['ERROR'] = []
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['TRACEBACK'] = ''
                pp['TIMING'] = 0
                pp['FINISHED'] = True
                pp['SUCCESS'] = False
                pp['PID'] = None
                pp['PASSED'] = False
                pp['STATE'] = 'SKIPPED:PRERUN'
                return_dict[priority] = pp
                # deal with a master not passing
                #   we cannot idely skip master files
                if not run_item.master:
                    continue
            # --------------------------------------------------------------
            # start time
            starttime = time.time()
            # try to run the main function
            # noinspection PyBroadException
            try:
                # ----------------------------------------------------------
                # run main function of module
                ll_item = modulemain(**kwargs)
                # ----------------------------------------------------------
                # close all plotting
                plotter = plotting.Plotter(params, recipe)
                plotter.closeall()
                # keep only some parameters
                llparams = ll_item['params']
                llrecipe = ll_item['recipe']
                pp['PID'] = deepcopy(llparams.get('PID', 'None'))
                pp['ERROR'] = deepcopy(llparams.get('LOGGER_ERROR', []))
                pp['WARNING'] = deepcopy(llparams.get('LOGGER_WARNING', []))
                pp['OUTPUTS'] = deepcopy(llrecipe.output_files)
                pp['TRACEBACK'] = []
                pp['SUCCESS'] = bool(ll_item.get('success', False))
                pp['PASSED'] = bool(ll_item.get('passed', False))
                pp['STATE'] = 'RETURN'
                # delete ll_item
                del llparams
                del ll_item
                # flag finished
                finished = pp['SUCCESS']
            # --------------------------------------------------------------
            # Manage debug exit interrupt errors
            except drs_exceptions.DebugExit as _:
                # deal with returns
                pp['PID'] = None
                pp['ERROR'] = []
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['TRACEBACK'] = ''
                pp['SUCCESS'] = False
                pp['PASSED'] = False
                pp['STATE'] = 'EXCEPTION:DEBUG'
                # flag not finished
                finished = False
                # deal with setting event (if it is defined -- only defined
                #    for parallel sessions)
                if event is not None:
                    event.set()
            # --------------------------------------------------------------
            # Manage Keyboard interrupt errors
            except KeyboardInterrupt:
                # deal with returns
                pp['PID'] = None
                pp['ERROR'] = []
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['TRACEBACK'] = ''
                pp['SUCCESS'] = False
                pp['PASSED'] = False
                pp['STATE'] = 'EXCEPTION:KeyboardInterrupt'
                # flag not finished
                finished = False
                # deal with setting event (if it is defined -- only defined
                #    for parallel sessions)
                if event is not None:
                    event.set()
            # --------------------------------------------------------------
            # Manage expected errors
            except drs_exceptions.LogExit as e:
                emsgs = [textdict['00-503-00005'].format(priority)]
                for emsg in e.errormessage.split('\n'):
                    emsgs.append('\n' + emsg)
                WLOG(params, 'warning', emsgs)
                pp['PID'] = None
                pp['ERROR'] = emsgs
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['SUCCESS'] = False
                pp['PASSED'] = False
                pp['STATE'] = 'EXCEPTION:LogExit'
                # expected error does not need traceback
                pp['TRACEBACK'] = []
                # flag not finished
                finished = False
            # --------------------------------------------------------------
            # Manage unexpected errors
            except Exception as e:
                # noinspection PyBroadException
                try:
                    import traceback
                    string_traceback = traceback.format_exc()
                except Exception as _:
                    string_traceback = ''
                emsgs = [textdict['00-503-00004'].format(priority)]
                for emsg in str(e).split('\n'):
                    emsgs.append('\n' + emsg)
                WLOG(params, 'warning', emsgs)
                pp['PID'] = None
                pp['ERROR'] = emsgs
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['SUCCESS'] = False
                pp['TRACEBACK'] = str(string_traceback)
                pp['PASSED'] = False
                pp['STATE'] = 'EXCEPTION:UNEXPECTED'
                # flag not finished
                finished = False
            # --------------------------------------------------------------
            # Manage unexpected errors
            except SystemExit as e:
                # noinspection PyBroadException
                try:
                    import traceback
                    string_traceback = traceback.format_exc()
                except Exception as _:
                    string_traceback = ''
                emsgs = [textdict['00-503-00015'].format(priority)]
                for emsg in str(e).split('\n'):
                    emsgs.append('\n' + emsg)
                WLOG(params, 'warning', emsgs)
                pp['PID'] = None
                pp['ERROR'] = emsgs
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['TRACEBACK'] = str(string_traceback)
                pp['SUCCESS'] = False
                pp['PASSED'] = False
                pp['STATE'] = 'EXCEPTION:SystemExit'
                # flag not finished
                finished = False
            # --------------------------------------------------------------
            # end time
            endtime = time.time()
            # add timing to pp
            pp['TIMING'] = endtime - starttime
        # ------------------------------------------------------------------
        # set finished flag
        pp['FINISHED'] = finished
        # ------------------------------------------------------------------
        # if STOP_AT_EXCEPTION and not finished stop here
        if stop_at_exception and not finished:
            if event is not None:
                wargs = [run_item.recipename]
                WLOG(params, 'debug', TextEntry('90-503-00008', args=wargs))
                event.set()
        # ------------------------------------------------------------------
        # append to return dict
        return_dict[priority] = pp
    # return the output array
    return return_dict


def _multi_process(params, recipe, runlist, cores, groupname=None):
    # first try to group tasks
    grouplist, groupnames = _group_tasks1(runlist, cores)
    # start process manager
    manager = Manager()
    event = Event()
    return_dict = manager.dict()
    # loop around groups
    #   - each group is a unique recipe
    for g_it, group in enumerate(grouplist):
        # process storage
        jobs = []
        # log progress
        _group_progress(params, g_it, grouplist, groupnames[g_it])
        # skip groups if event is set
        if event.is_set():
            # TODO: Add to language db
            WLOG(params, 'warning', '\tSkipping group')
            continue
        # loop around sub groups
        #    - each sub group is a set of runs of the same recipe
        #    - there are "number of cores" number of these subgroups
        for r_it, runlist_group in enumerate(group):
            # get args
            args = [params, recipe, runlist_group, return_dict, r_it + 1,
                    cores, event, groupname]
            # get parallel process
            process = Process(target=_linear_process, args=args)
            process.start()
            jobs.append(process)
        # do not continue until finished
        for pit, proc in enumerate(jobs):
            # TODO: remove or add to language db
            WLOG(params, 'debug', 'MULTIPROCESS - joining job {0}'.format(pit))
            proc.join()

    # return return_dict
    return dict(return_dict)


# TODO: remove or replace _multi_process
def _multi_process1(params, recipe, runlist, cores, groupname=None):
    # first try to group tasks (now just by recipe)
    grouplist, groupnames = _group_tasks2(runlist, cores)
    # start process manager
    manager = Manager()
    event = manager.Event()
    return_dict = manager.dict()
    # loop around groups
    #   - each group is a unique recipe
    for g_it, groupnum in enumerate(grouplist):
        # get this groups values
        group = grouplist[groupnum]
        # log progress
        _group_progress(params, g_it, grouplist, groupnames[groupnum])
        # skip groups if event is set
        if event.is_set():
            # TODO: Add to language db
            WLOG(params, 'warning', '\tSkipping group')
            continue
        # list of params for each entry
        params_per_process = []
        # populate params for each sub group
        for r_it, runlist_group in enumerate(group):
            args = [params, recipe, runlist_group, return_dict, r_it + 1,
                    cores, event, groupname]
            params_per_process.append(args)
        # start parellel jobs
        pool = Pool(cores)
        pool.starmap(_linear_process, params_per_process)
    # return return_dict
    return dict(return_dict)


# =============================================================================
# Define working functions
# =============================================================================
def _get_non_telluric_stars(params, table, tstars: List[str]) -> List[str]:
    """
    Takes a table and gets all objects (OBJ_DARK and OBJ_FP) that are not in
    tstars (telluric stars)

    :param params:
    :param table:
    :param tstars:
    :return:
    """
    # add to debug log
    WLOG(params, 'debug', TextEntry('90-503-00015'))
    # deal with no tstars
    if drs_text.null_text(tstars, ['None', '']):
        tstars = []
    # deal with no table
    #    (can happen when coming from mk_tellu_db or fit_tellu_db etc)
    if (table is None) or len(table) == 0:
        return []
    # ----------------------------------------------------------------------
    # lets narrow down our list
    # ----------------------------------------------------------------------
    # 1. keep only obj fp and obj dark files
    dprtype = table['KW_DPRTYPE']
    mask = (dprtype == 'OBJ_FP') | (dprtype == 'OBJ_DARK')
    # 2. keep only obstype = OBJECT
    mask &= table['KW_OBSTYPE'] == 'OBJECT'
    # get all object names from all object columns
    raw_objects = []
    for col in table.colnames:
        if col in OBJNAMECOLS:
            raw_objects += list(table[col][mask])
    # make a unique list of names
    all_objects = np.unique(raw_objects)
    # now find all those not in tstars
    other_objects = []
    # loop around all objects
    for objname in all_objects:
        # do not add telluric stars
        if objname not in tstars:
            other_objects.append(objname)
    # add to debug log
    WLOG(params, 'debug', TextEntry('90-503-00016', args=[len(other_objects)]))
    # return other objects
    return list(np.sort(other_objects))


def _update_table_objnames(params, table):
    """
    Takes a table and forces updates to object name columns

    :param params:
    :param table:
    :return:
    """
    # get pseudo constants
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    # loop around columns
    for col in table.colnames:
        if col in OBJNAMECOLS:
            # need to map values by new drs obj name
            table[col] = list(map(pconst.DRS_OBJ_NAME, list(table[col])))
    # return table
    return table


def _get_recipe_module(params, **kwargs):
    func_name = __NAME__ + '.get_recipe_module()'
    # log progress: loading recipe module files
    WLOG(params, '', TextEntry('40-503-00014'))
    # get parameters from params/kwargs
    instrument = pcheck(params, 'INSTRUMENT', 'instrument', kwargs, func_name)
    instrument_path = pcheck(params, 'DRS_MOD_INSTRUMENT_CONFIG',
                             'instrument_path', kwargs, func_name)
    core_path = pcheck(params, 'DRS_MOD_CORE_CONFIG', 'core_path', kwargs,
                       func_name)
    # deal with no instrument
    if drs_text.null_text(instrument, ['None', '']):
        ipath = core_path
        instrument = None
    else:
        ipath = instrument_path
    # else we have a name and an instrument
    margs = [instrument, ['recipe_definitions.py'], ipath, core_path]
    modules = constants.getmodnames(*margs, return_paths=False)
    # load module
    mod = constants.import_module(func_name, modules[0], full=True)
    # return module
    return mod


def _get_rvalues(runtable):
    return list(map(lambda x: x.upper(), runtable.values()))


def _check_runtable(params, runtable, recipemod):
    func_name = __NAME__ + '._check_runtable()'
    # get recipe list
    recipelist = list(map(lambda x: x.name, recipemod.get().recipes))
    # remove .py
    recipelist = np.char.replace(recipelist, '.py', '')
    # check that all run items start with a recipe
    for runkey in runtable:
        # get this iterations run item
        run_item = runtable[runkey]
        # get the program (should be the first word in the run_item)
        program = run_item.split(' ')[0].replace('.py', '')
        # make sure it is in recipelist
        if program not in recipelist:
            # log error
            eargs = [program, params['INSTRUMENT'], func_name]
            WLOG(params, 'error', TextEntry('00-503-00011', args=eargs))


def _get_filters(params, srecipe):
    # set up function name
    func_name = __NAME__ + '._get_filters()'
    # get pseudo constatns
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    # set up filter storage
    filters = dict()
    # loop around recipe filters
    for key in srecipe.filters:
        # get value
        value = srecipe.filters[key]
        # deal with list
        if isinstance(value, list):
            filters[key] = value
        # if this is in params set this value - these are dealing with
        #  object names
        elif (value in params) and (value in SPECIAL_LIST_KEYS):
            # get values from
            user_filter = params[value]
            # deal with unset value
            slvalues = ['ALL', 'NONE']
            if (user_filter is None) or (user_filter.upper() in slvalues):
                if value == 'TELLURIC_TARGETS':
                    wlist = telluric.get_whitelist(params)
                    # note we need to update this list to match
                    # the cleaning that is done in preprocessing
                    cwlist = list(map(pconst.DRS_OBJ_NAME, wlist))
                    # add cleaned obj list to filters
                    filters[key] = list(cwlist)
                else:
                    continue
            # else assume we have a special list that is a string list
            #   (i.e. SCIENCE_TARGETS = "target1, target2, target3"
            elif isinstance(user_filter, str):
                wlist =  _split_string_list(user_filter)
                # note we need to update this list to match
                # the cleaning that is done in preprocessing
                cwlist = list(map(pconst.DRS_OBJ_NAME, wlist))
                # add cleaned obj list to filters
                filters[key] = list(cwlist)
                if value == 'SCIENCE_TARGETS':
                    # update science targets
                    params.set('SCIENCE_TARGETS', value=', '.join(cwlist))
            else:
                continue
        # else assume we have a straight string to look for (if it is a valid
        #   string)
        elif isinstance(value, str):
            filters[key] = value
        # if we don't have a valid string cause an error
        else:
            # log error
            eargs = [key, value, srecipe.name, func_name]
            WLOG(params, 'error', TextEntry('00-503-00017', args=eargs))
    # return filters
    return filters


def _split_string_list(string):
    if ';' in string:
        return string.split(';')
    elif ',' in string:
        return string.split(',')
    else:
        return string.split(' ')


def _get_cores(params):
    # get cores from inputs
    if 'CORES' in params['INPUTS']:
        # get value from inputs
        cores = params['INPUTS']['CORES']
        # only update params if cores is not None
        if not drs_text.null_text(cores, ['None', '']):
            try:
                cores = int(cores)
            except ValueError as e:
                eargs = [params['CORES'], type(e), e]
                WLOG(params, 'error', TextEntry('00-503-00013', args=eargs))
                cores = 1
            except Exception as e:
                eargs = [type(e), e]
                WLOG(params, 'error', TextEntry('00-503-00014', args=eargs))
                cores = 1
            # update the value in params
            params.set('CORES', value=cores, source='USER INPUT')

    # get number of cores
    if 'CORES' in params:
        try:
            cores = int(params['CORES'])
        except ValueError as e:
            eargs = [params['CORES'], type(e), e]
            WLOG(params, 'error', TextEntry('00-503-00006', args=eargs))
            cores = 1
        except Exception as e:
            eargs = [type(e), e]
            WLOG(params, 'error', TextEntry('00-503-00007', args=eargs))
            cores = 1
    else:
        cores = 1
    # get number of cores on machine
    cpus = multiprocessing.cpu_count()
    # check that cores is valid
    if cores < 1:
        WLOG(params, 'error', TextEntry('00-503-00008', args=[cores]))
    if cores >= cpus:
        eargs = [cpus, cores]
        WLOG(params, 'error', TextEntry('00-503-00009', args=eargs))
    # return number of cores
    return cores


def _group_progress(params, g_it, grouplist, groupname):
    # get message
    wargs = [' * ', g_it + 1, len(grouplist), groupname]
    # log
    WLOG(params, 'info', '', colour='magenta')
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    WLOG(params, 'info', TextEntry('40-503-00018', args=wargs),
         colour='magenta')
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    WLOG(params, 'info', '', colour='magenta')


def _group_tasks(runlist, cores):
    # individual runs of the same recipe are independent of each other

    # get all recipe names
    recipenames = []
    for it, run_item in enumerate(runlist):
        recipenames.append(run_item.shortname)
    # storage of groups
    groups = dict()
    names = dict()
    group_number = 0
    # loop around runlist
    for it, run_item in enumerate(runlist):
        # get recipe name
        recipe = run_item.shortname
        # if it is the first item must have a new group
        if it == 0:
            groups[group_number] = [run_item]
        else:
            if recipe == recipenames[it - 1]:
                groups[group_number].append(run_item)
            else:
                group_number += 1
                groups[group_number] = [run_item]
        # add the names
        names[group_number] = recipe
    # now we have the groups we can push into the core sub-groups
    out_groups = []
    out_names = []

    # loop around the different reipce groups
    for groupkey in groups:

        out_group = []
        group = groups[groupkey]
        out_name = names[groupkey]

        for it in range(cores):
            sub_group = group[it::cores]
            if len(sub_group) > 0:
                out_group.append(sub_group)

        out_groups.append(out_group)
        out_names.append(out_name)
    # return output groups
    return out_groups, out_names


# TODO: Remove or replace with _group_tasks
def _group_tasks1(runlist, cores):
    # individual runs of the same recipe are independent of each other

    # get all recipe names
    recipenames = []
    for it, run_item in enumerate(runlist):
        recipenames.append(run_item.shortname)
    # storage of groups
    groups = dict()
    names = dict()
    group_number = 0
    # loop around runlist
    for it, run_item in enumerate(runlist):
        # get recipe name
        recipe = run_item.shortname
        # if it is the first item must have a new group
        if it == 0:
            groups[group_number] = [run_item]
        else:
            cond1 = recipe == recipenames[it - 1]
            cond2 = len(groups[group_number]) < cores

            if cond1 and cond2:
                groups[group_number].append(run_item)
            else:
                group_number += 1
                groups[group_number] = [run_item]
        # add the names
        names[group_number] = recipe
    # now we have the groups we can push into the core sub-groups
    out_groups = []
    out_names = []

    # loop around the different reipce groups
    for groupkey in groups:

        out_group = []
        group = groups[groupkey]
        out_name = names[groupkey]

        for it in range(cores):
            sub_group = group[it::cores]
            if len(sub_group) > 0:
                out_group.append(sub_group)

        out_groups.append(out_group)
        out_names.append(out_name)
    # return output groups
    return out_groups, out_names


# TODO: Remove or replace with _group_tasks
def _group_tasks2(runlist, cores):
    # individual runs of the same recipe are independent of each other

    # get all recipe names
    recipenames = []
    for it, run_item in enumerate(runlist):
        recipenames.append(run_item.shortname)
    # storage of groups
    groups = dict()
    names = dict()
    group_number = 0
    # loop around runlist
    for it, run_item in enumerate(runlist):
        # get recipe name
        recipe = run_item.shortname
        # if it is the first item must have a new group
        if it == 0:
            groups[group_number] = [run_item]
        else:
            if recipe == recipenames[it - 1]:
                groups[group_number].append(run_item)
            else:
                group_number += 1
                groups[group_number] = [run_item]
        # add the names
        names[group_number] = recipe

    # return output groups
    return groups, names


def _remove_engineering(params, ftable):
    global REMOVE_ENG_NIGHTS
    # if we are dealing with the trigger run do not do this -- user has
    #   specified a night
    if params['INPUTS']['TRIGGER']:
        return ftable
    # get nightnames
    nightnames = ftable['__NIGHTNAME']
    obstypes = ftable['KW_OBSTYPE']
    # get unique nights
    u_nights = np.unique(nightnames)
    # get the object mask (i.e. we want to know that we have objects for this
    #   night
    objmask = obstypes == 'OBJECT'
    # define empty keep mask
    keepmask = np.zeros(len(ftable), dtype=bool)
    # loop around nights
    for night in u_nights:
        # get night mask
        nightmask = nightnames == night
        # joint mask
        nightobjmask = nightmask & objmask
        # if we find objects then keep all files from this night
        if np.sum(nightobjmask) > 0:
            # add to keep mask
            keepmask[nightmask] = True
        elif night not in REMOVE_ENG_NIGHTS:
            # log message
            WLOG(params, 'warning', TextEntry('10-503-00014', args=[night]))
            # add to remove eng nights (so log message not produced again)
            REMOVE_ENG_NIGHTS.append(night)

    # return masked ftable
    return ftable[keepmask]


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

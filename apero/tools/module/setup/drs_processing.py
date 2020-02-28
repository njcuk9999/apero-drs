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
import copy
import time
from astropy.table import Table
from collections import OrderedDict
import multiprocessing
from multiprocessing import Pool, Process, Manager, Event

from apero import core
from apero.core.core import drs_startup
from apero.core.core import drs_log
from apero import locale
from apero.locale import drs_exceptions
from apero.core import constants
from apero import plotting
from apero.io import drs_table
from apero.io import drs_path
from apero.io import drs_fits
from apero.io import drs_lock
from apero.tools.module.setup import drs_reset
from apero.science import telluric
from apero.science import preprocessing

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_processing.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck

# Run keys
RUN_KEYS = dict()
RUN_KEYS['RUN_NAME'] = 'Run Unknown'
RUN_KEYS['SEND_EMAIL'] = 'False'
RUN_KEYS['EMAIL_ADDRESS'] = None
RUN_KEYS['NIGHT_NAME'] = None
RUN_KEYS['BNIGHTNAMES'] = None
RUN_KEYS['WNIGHTNAMES'] = None
RUN_KEYS['MASTER_NIGHT'] = None
RUN_KEYS['CORES'] = 1
RUN_KEYS['STOP_AT_EXCEPTION'] = False
RUN_KEYS['TEST_RUN'] = False
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


# =============================================================================
# Define classes
# =============================================================================
class Run:
    def __init__(self, params, runstring, mod=None, priority=0, inrecipe=None):
        self.params = params
        self.runstring = runstring
        self.priority = priority
        self.args = []
        self.recipename = ''
        self.runname = None
        self.skipname = None
        self.recipe = inrecipe
        self.module = mod
        self.master = False
        self.recipemod = None
        self.kwargs = dict()
        self.fileargs = dict()
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
                    if self.kwargs[kwargname] in [None, 'None']:
                        del self.kwargs[kwargname]
                    # option 2: the argument is empty --> del argument
                    elif len(self.kwargs[kwargname]) == 0:
                        del self.kwargs[kwargname]
                    # option 3: we have an arugment --> use argument (but
                    #           remove DrsFitsFile instance - we only need the
                    #           string filename
                    else:
                        self.kwargs[kwargname] = self.kwargs[kwargname][0]

    def find_recipe(self, mod=None):
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
    rlist = generate_run_list(params, None, runtable)
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
        if params['INPUTS']['NIGHTNAME'] not in ['None', '', None]:
            params['NIGHTNAME'] = params['INPUTS']['NIGHTNAME']
    # make sure nightname is str or None
    if params['NIGHTNAME'] in ['None', '']:
        params['NIGHTNAME'] = None
    # ----------------------------------------------------------------------
    # nightname blacklist
    if 'BNIGHTNAMES' in params['INPUTS']:
        if params['INPUTS']['BNIGHTNAMES'] not in ['None', '', None]:
            params['BNIGHTNAMES'] = params['INPUTS'].listp('BNIGHTNAMES')
    # ----------------------------------------------------------------------
    # nightname whitelist
    if 'WNIGHTNAMES' in params['INPUTS']:
        if params['INPUTS']['WNIGHTNAMES'] not in ['None', '', None]:
            params['WNIGHTNAMES'] = params['INPUTS'].listp('WNIGHTNAMES')
    # ----------------------------------------------------------------------
    # deal with having a file specified
    params['FILENAME'] = None
    if 'FILENAME' in params['INPUTS']:
        if params['INPUTS']['FILENAME'] not in ['None', '', None]:
            if isinstance(params['INPUTS']['FILENAME'], str):
                params['FILENAME'] = params['INPUTS'].listp('FILENAME')
            else:
                params['FILENAME'] = params['INPUTS']['FILENAME']
    # ----------------------------------------------------------------------
    # deal with getting test run from user input
    if 'TEST' in params['INPUTS']:
        test = params['INPUTS']['TEST']
        if test not in ['', 'None', None]:
            if test.upper() in ['TRUE', '1']:
                params['TEST_RUN'] = True
            else:
                params['TEST_RUN'] = False

    # ----------------------------------------------------------------------
    # relock params
    params.lock()
    # ----------------------------------------------------------------------
    # return parameter dictionary and runtable
    return params, runtable


def fix_run_file(runfile):
    # only do this if we have a runfile
    if os.path.exists(runfile):
        # open run file
        runf = open(runfile, 'r')
        # read all lines
        lines = runf.readlines()
        # close file
        runf.close()
        # convert to character array
        lines = np.char.array(lines)
        # replace all equal signs
        lines = lines.replace('=', '@' * 50, 1)
        lines = lines.replace('=', ' ')
        lines = lines.replace('@' * 50, '=')
        # open run file
        runf = open(runfile, 'w')
        # write to file
        for line in lines:
            runf.write(line + '\n')
        # close file
        runf.close()


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


def find_raw_files(params, recipe, **kwargs):
    func_name = __NAME__ + '.find_raw_files()'
    # get properties from params
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', 'absfile_col', kwargs,
                         func_name)
    modified_col = pcheck(params, 'REPROCESS_MODIFIEDCOL', 'modified_col',
                          kwargs, func_name)
    sortcol = pcheck(params, 'REPROCESS_SORTCOL_HDRKEY', 'sortcol', kwargs,
                     func_name)
    raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE', 'raw_index_file',
                            kwargs, func_name)
    itable_filecol = pcheck(params, 'DRS_INDEX_FILENAME', 'itable_filecol',
                            kwargs, func_name)
    # get path
    path, rpath = _get_path_and_check(params, 'DRS_DATA_RAW')

    # print progress
    WLOG(params, 'info', TextEntry('40-503-00010'))

    # get files
    gfout = _get_files(params, recipe, path, rpath)
    nightnames, filelist, basenames, mod_times, mkwargs = gfout

    # construct a table
    mastertable = Table()
    mastertable[night_col] = nightnames
    mastertable[itable_filecol] = basenames
    mastertable[absfile_col] = filelist
    mastertable[modified_col] = mod_times
    for kwarg in mkwargs:
        mastertable[kwarg] = mkwargs[kwarg]
    # sort by sortcol
    sortmask = np.argsort(mastertable[sortcol])
    mastertable = mastertable[sortmask]
    # save master table
    mpath = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
    mastertable.write(mpath, overwrite=True)
    # return the file list
    return mastertable, rpath


def generate_run_list(params, table, runtable):
    # print progress: generating run list
    WLOG(params, 'info', TextEntry('40-503-00011'))
    # get recipe defintions module (for this instrument)
    recipemod = _get_recipe_module(params)
    # get all values (upper case) using map function
    rvalues = _get_rvalues(runtable)
    # check if rvalues has a run sequence
    sequencelist = _check_for_sequences(rvalues, recipemod)
    # set rlist to None (for no sequences)
    rlist = None
    # if we have found sequences need to deal with them
    if sequencelist is not None:
        # loop around sequences
        for sequence in sequencelist:
            # log progress
            WLOG(params, '', TextEntry('40-503-00009', args=[sequence[0]]))
            # generate new runs for sequence
            newruns = _generate_run_from_sequence(params, sequence, table)
            # update runtable with sequence generation
            runtable, rlist = _update_run_table(sequence, runtable, newruns)
    # all runtable elements should now be in recipe list
    _check_runtable(params, runtable, recipemod)
    # return Run instances for each runtable element
    return generate_ids(params, runtable, recipemod, rlist)


def process_run_list(params, recipe, runlist, group=None):
    # get number of cores
    cores = _get_cores(params)
    # pipe to correct module
    if cores == 1:
        # log process: Running with 1 core
        WLOG(params, 'info', TextEntry('40-503-00016'))
        # run as linear process
        rdict = _linear_process(params, recipe, runlist, group)
    else:
        # log process: Running with N cores
        WLOG(params, 'info', TextEntry('40-503-00017', args=[cores]))
        # run as multiple processes
        rdict = _multi_process(params, recipe, runlist, cores, group)

    # remove lock files
    drs_lock.reset_lock_dir(params)

    # convert to ParamDict and set all sources
    odict = OrderedDict()
    keys = np.sort(np.array(list(rdict.keys())))
    for key in keys:
        odict[key] = ParamDict(rdict[key])

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
        out_txt_table = open(out_txt_path, 'w')
        for value in runlists:
            out_txt_table.write(value + '\n')
        out_txt_table.close()
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
def generate_ids(params, runtable, mod, rlist=None, **kwargs):
    func_name = __NAME__ + '.generate_ids()'
    # get keys from params
    run_key = pcheck(params, 'REPROCESS_RUN_KEY', 'run_key', kwargs, func_name)
    # should just need to sort these
    numbers = np.array(list(runtable.keys()))
    commands = np.array(list(runtable.values()))
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
        # deal with skip
        skip, reason = skip_run_object(params, run_object)
        # deal with passing debug
        if params['DRS_DEBUG'] > 0:
            dargs = [run_object.runstring, params['DRS_DEBUG']]
            run_object.runstring = '{0} --debug={1}'.format(*dargs)
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


def skip_run_object(params, runobj):
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
            infiledef = recipe.filemod.raw_file
        elif runobj.kind == 1:
            infiledef = recipe.filemod.pp_file
        else:
            infiledef = recipe.filemod.out_file
        # ------------------------------------------------------------------
        # add required properties to infile
        infile = infiledef.newcopy(recipe=recipe)
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
            outfile = output.newcopy(recipe=recipe)
            # --------------------------------------------------------------
            # check whether we need to add fibers
            if output.fibers is not None:
                # loop around fibers
                for fiber in output.fibers:
                    # construct file name
                    outfile.construct_filename(params, infile=infile,
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
                outfile.construct_filename(params, infile=infile, path=outpath,
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
    all_sequences = mod.sequences
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
    # get all telluric stars
    tstars, wfilename = telluric.get_whitelist(params)
    # get filemod and recipe mod
    pconst = constants.pload(params['INSTRUMENT'])
    filemod = pconst.FILEMOD()
    recipemod = pconst.RECIPEMOD()
    # generate sequence
    sequence[1].process_adds(params, tstars=list(tstars))
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
            srecipe.recipemod = recipemod
        if srecipe.filemod is None:
            srecipe.filemod = filemod
        # ------------------------------------------------------------------
        # copy table
        # ------------------------------------------------------------------
        ftable = Table(table)

        # ------------------------------------------------------------------
        # deal with black and white lists
        # ------------------------------------------------------------------
        # black list
        if params['BNIGHTNAMES'] not in ['', 'None', None]:
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
        if params['WNIGHTNAMES'] not in ['', 'None', None]:
            # start by assuming we want to keep nothing
            mask = np.zeros(len(ftable), dtype=bool)
            # get black list from params
            whitelist_nights = params.listp('WNIGHTNAMES', dtype=str)
            # loop around black listed nights and set them to False
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

        elif params['NIGHTNAME'] not in ['', 'None', None]:
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
        sruns = srecipe.generate_runs(params, ftable, filters=filters,
                                      allowedfibers=allowedfibers)
        # append runs to new runs list
        for srun in sruns:
            newruns.append([srun, srecipe])
    # return all new runs
    return newruns


def _update_run_table(sequence, runtable, newruns):
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
            recipe_list[idnumber] = None
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
            # log which core is being used (only if using multiple cores)
            if cores > 1:
                WLOG(params, 'info', wmsg, colour='magenta', wrap=False)
            else:
                WLOG(params, 'info', wmsg, colour='magenta', wrap=False)
            # add default outputs
            pp['ERROR'] = []
            pp['WARNING'] = []
            pp['OUTPUTS'] = dict()
            pp['TIMING'] = None
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
            pp['ERROR'] = []
            pp['WARNING'] = []
            pp['OUTPUTS'] = dict()
            pp['TRACEBACK'] = ''
            pp['SUCCESS'] = False
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
                pp['ERROR'] = copy.deepcopy(llparams['LOGGER_ERROR'])
                pp['WARNING'] = copy.deepcopy(llparams['LOGGER_WARNING'])
                pp['OUTPUTS'] = copy.deepcopy(llrecipe.output_files)
                pp['TRACEBACK'] = []
                pp['SUCCESS'] = bool(ll_item['success'])
                # delete ll_item
                del llparams
                del ll_item
                # flag finished
                finished = pp['SUCCESS']
            # --------------------------------------------------------------
            # Manage debug exit interrupt errors
            except drs_exceptions.DebugExit as _:
                # deal with returns
                pp['ERROR'] = []
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['TRACEBACK'] = ''
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
                pp['ERROR'] = []
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['TRACEBACK'] = ''
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
                pp['ERROR'] = emsgs
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
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
                pp['ERROR'] = emsgs
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['TRACEBACK'] = str(string_traceback)
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
                pp['ERROR'] = emsgs
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
                pp['TRACEBACK'] = str(string_traceback)
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
    if instrument == 'None' or instrument is None:
        ipath = core_path
        instrument = None
    else:
        ipath = instrument_path
    # else we have a name and an instrument
    margs = [instrument, ['recipe_definitions.py'], ipath, core_path]
    modules = constants.getmodnames(*margs, path=False)
    # load module
    mod = constants.import_module(func_name, modules[0], full=True)
    # return module
    return mod


def _get_rvalues(runtable):
    return list(map(lambda x: x.upper(), runtable.values()))


def _check_runtable(params, runtable, recipemod):
    func_name = __NAME__ + '._check_runtable()'
    # get recipe list
    recipelist = list(map(lambda x: x.name, recipemod.recipes))
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


def _get_path_and_check(params, key):
    # check key in params
    if key not in params:
        WLOG(params, 'error', '{0} not found in params'.format(key))
    # get top level path to search
    rpath = params[key]
    # deal with not having nightname
    if 'NIGHTNAME' not in params:
        path = str(rpath)
    elif params['NIGHTNAME'] not in ['', 'None', None]:
        path = os.path.join(rpath, params['NIGHTNAME'])
    else:
        path = str(rpath)
    # check if path exists
    if not os.path.exists(path):
        WLOG(params, 'error', 'Path {0} does not exist'.format(path))
    else:
        return path, rpath


def _get_files(params, recipe, path, rpath, **kwargs):
    func_name = __NAME__ + '.get_files()'
    # get properties from params
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', 'absfile_col', kwargs,
                         func_name)
    modified_col = pcheck(params, 'REPROCESS_MODIFIEDCOL', 'modified_col',
                          kwargs, func_name)
    raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE', 'raw_index_file',
                            kwargs, func_name)
    # get the file filter (should be None unless we want specific files)
    filefilter = params.get('FILENAME', None)
    if filefilter is not None:
        filefilter = list(params['FILENAME'])
    # ----------------------------------------------------------------------
    # get the pseudo constant object
    pconst = constants.pload(params['INSTRUMENT'])
    # ----------------------------------------------------------------------
    # get header keys
    headerkeys = pconst.RAW_OUTPUT_KEYS()
    # get raw valid files
    raw_valid = pconst.VALID_RAW_FILES()
    # ----------------------------------------------------------------------
    # storage list
    filelist, basenames, nightnames, mod_times = [], [], [], []
    # load raw index
    rawindexfile = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
    if os.path.exists(rawindexfile):
        rawindex = drs_table.read_table(params, rawindexfile, fmt='fits')
    else:
        rawindex = None
    # ----------------------------------------------------------------------
    # populate the storage dictionary
    kwargs = dict()
    for key in headerkeys:
        kwargs[key] = []
    # ----------------------------------------------------------------------
    # get files (walk through path)
    for root, dirs, files in os.walk(path):
        # loop around files in this root directory
        for filename in files:
            # --------------------------------------------------------------
            if filefilter is not None:
                if os.path.basename(filename) not in filefilter:
                    continue
            # --------------------------------------------------------------
            # get night name
            ucpath = drs_path.get_uncommon_path(rpath, root)
            if ucpath is None:
                eargs = [path, rpath, func_name]
                WLOG(params, 'error', TextEntry('00-503-00003', args=eargs))
            # --------------------------------------------------------------
            # make sure file is valid
            isvalid = False
            for suffix in raw_valid:
                if filename.endswith(suffix):
                    isvalid = True
            # --------------------------------------------------------------
            # do not scan empty ucpath
            if len(ucpath) == 0:
                continue
            # --------------------------------------------------------------
            # log the night directory
            if ucpath not in nightnames:
                WLOG(params, '', TextEntry('40-503-00003', args=[ucpath]))
            # --------------------------------------------------------------
            # get absolute path
            abspath = os.path.join(root, filename)
            modified = os.path.getmtime(abspath)
            # --------------------------------------------------------------
            # if not valid skip
            if not isvalid:
                continue
            # --------------------------------------------------------------
            # else append to list
            else:
                nightnames.append(ucpath)
                filelist.append(abspath)
                basenames.append(filename)
                mod_times.append(modified)
            # --------------------------------------------------------------
            # see if file in raw index and has correct modified date
            if rawindex is not None:
                # find file
                rowmask = (rawindex[absfile_col] == abspath)
                # find match date
                rowmask &= modified == rawindex[modified_col]
                # only continue if both conditions found
                if np.sum(rowmask) > 0:
                    # locate file
                    row = np.where(rowmask)[0][0]
                    # if both conditions met load from raw fits file
                    for key in headerkeys:
                        kwargs[key].append(rawindex[key][row])
                    # file was found
                    rfound = True
                else:
                    rfound = False
            else:
                rfound = False
            # --------------------------------------------------------------
            # deal with header
            if filename.endswith('.fits') and not rfound:
                # read the header
                header = drs_fits.read_header(params, abspath)
                # fix the headers
                header = preprocessing.fix_header(params, recipe, header=header)
                # loop around header keys
                for key in headerkeys:
                    rkey = params[key][0]
                    if rkey in header:
                        kwargs[key].append(header[rkey])
                    else:
                        kwargs[key].append('')
    # ----------------------------------------------------------------------
    # return filelist
    return nightnames, filelist, basenames, mod_times, kwargs


def _get_filters(params, srecipe):
    filters = dict()
    # loop around recipe filters
    for key in srecipe.filters:
        # get value
        value = srecipe.filters[key]
        # deal with list
        if isinstance(value, list):
            filters[key] = value
        # if this is in params set this value
        elif value in params:
            # get values from
            user_filter = params[value]
            # deal with unset value
            if (user_filter is None) or (user_filter.upper() == 'NONE'):
                if value == 'TELLURIC_TARGETS':
                    wlist, wfilename = telluric.get_whitelist(params)
                    filters[key] = list(wlist)
                else:
                    continue
            elif isinstance(user_filter, str):
                filters[key] = _split_string_list(user_filter)
            else:
                continue
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
        if cores not in ['', 'None', None]:
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

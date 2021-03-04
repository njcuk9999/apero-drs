#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-06 at 11:57

@author: cook



"""
from astropy.table import Table
from collections import OrderedDict
from copy import deepcopy
import itertools
import numpy as np
import os
import sys
import time
from typing import Any, Dict, List, Tuple, Union
import warnings

from apero.base import base
from apero.core.core import drs_base_classes as base_class
from apero.core.core import drs_exceptions
from apero.core.core import drs_text
from apero.core.core import drs_log
from apero.core.core import drs_argument
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero import lang
from apero.core import constants
from apero.io import drs_table
from apero.io import drs_lock
from apero.science.preprocessing import gen_pp
from apero.science import telluric
from apero.tools.module.setup import drs_reset

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
# Get function string
display_func = drs_log.display_func
# get the parameter dictionary
ParamDict = constants.ParamDict
# get drs recipe
DrsRecipe = drs_recipe.DrsRecipe
DrsRecipeException = drs_recipe.DrsRecipeException
# get drs argument
DrsArgument = drs_argument.DrsArgument
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get database
IndexDatabase = drs_database.IndexDatabase
# Run keys
RUN_KEYS = dict()
RUN_KEYS['RUN_NAME'] = 'Run Unknown'
RUN_KEYS['SEND_EMAIL'] = False
RUN_KEYS['EMAIL_ADDRESS'] = None
RUN_KEYS['OBS_DIR'] = None
RUN_KEYS['EXCLUDE_OBS_DIRS'] = None
RUN_KEYS['INCLUDE_OBS_DIRS'] = None
RUN_KEYS['PI_NAMES'] = None
RUN_KEYS['MASTER_OBS_DIR'] = None
RUN_KEYS['UPDATE_OBJ_DATABASE'] = False
RUN_KEYS['CORES'] = 1
RUN_KEYS['STOP_AT_EXCEPTION'] = False
RUN_KEYS['TEST_RUN'] = False
RUN_KEYS['TRIGGER_RUN'] = False
RUN_KEYS['USE_ODO_REJECTLIST'] = True
RUN_KEYS['RECAL_TEMPLATES'] = False
RUN_KEYS['ENGINEERING'] = False
RUN_KEYS['RESET_ALLOWED'] = False
RUN_KEYS['RESET_TMP'] = False
RUN_KEYS['RESET_REDUCED'] = False
RUN_KEYS['RESET_CALIB'] = False
RUN_KEYS['RESET_TELLU'] = False
RUN_KEYS['RESET_LOG'] = False
RUN_KEYS['RESET_PLOT'] = False
RUN_KEYS['RESET_RUN'] = False
RUN_KEYS['TELLURIC_TARGETS'] = None
RUN_KEYS['SCIENCE_TARGETS'] = None
# storage for reporting removed engineering directories
REMOVE_ENG_DIRS = []
# get special list from recipes
SPECIAL_LIST_KEYS = drs_recipe.SPECIAL_LIST_KEYS
# get list of obj name cols
OBJNAMECOL = 'KW_OBJNAME'
# list of arguments to remove from skip check
SKIP_REMOVE_ARGS = ['--skip', '--program', '--debug', '--plot', '--shortname']
# keep a global copy of plt
PLT_MOD = None


# =============================================================================
# Define classes
# =============================================================================
class Run:
    def __init__(self, params, indexdb: IndexDatabase, runstring,
                 mod: Union[base_class.ImportModule, None] = None,
                 priority=0, inrecipe=None):
        self.params = params
        self.indexdb = indexdb
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
        self.block_kind = None
        self.obs_dir = None
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
            WLOG(None, 'error', textentry('00-007-00001', args=eargs))
        # else return
        return recipe, mod

    def get_recipe_kind(self):
        # the first argument must be the recipe name
        self.recipename = self.args[0]
        # make sure recipe does not have .py on the end
        self.recipename = _remove_py(self.recipename)
        # get a drs path instance
        path_inst = drs_file.DrsPath(self.params, _update=False)
        blocks = path_inst.block_names()
        # get recipe type (raw/tmp/reduced)
        if self.recipe.in_block_str in blocks:
            self.block_kind = str(self.recipe.in_block_str)
        else:
            emsg1 = ('RunList Error: Recipe = "{0}" invalid'
                     ''.format(self.recipename))
            emsg2 = '\t Line: {0} {1}'.format(self.priority, self.runstring)
            WLOG(self.params, 'error', [emsg1, emsg2])

    def get_obs_dir(self):
        if 'obs_dir' in self.recipe.args:
            # get directory position
            pos = int(self.recipe.args['obs_dir'].pos) + 1
            # set
            self.obs_dir = self.args[pos]
        else:
            self.obs_dir = ''

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
        self.kwargs = self.recipe.recipe_setup(self.indexdb, inargs=self.args)
        # deal with arguments that should be user defined only
        for kwarg in self.recipe.kwargs:
            # argument must be in kwargs (after recipe setup)
            if kwarg in self.kwargs:
                # if dtype in these dtypes it is user only
                if self.recipe.kwargs[kwarg].dtype in ['switch']:
                    # remove keyword
                    del self.kwargs[kwarg]
        # add argument to set program name
        pargs = [self.recipe.shortname, int(self.priority)]
        # add argument --program
        self.kwargs['program'] = '{0}[{1:05d}]'.format(*pargs)
        # add argument --shortname
        self.kwargs['shortname'] = str(self.recipe.shortname)
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
        self.get_obs_dir()
        # populate a list of reciped arguments
        for kwarg in self.recipe.kwargs:
            # only add required arguments
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
        path_inst = drs_file.DrsPath(params, block_kind=recipe.in_block_str)
        input_dir = path_inst.abspath
        # check whether input directory exists
        if not os.path.exists(input_dir):
            wargs = [input_dir]
            WLOG(params, 'warning', textentry('10-503-00008', args=wargs))
            return False
        # ------------------------------------------------------------------
        # if we have a directory add it to the input dir
        if 'obs_dir' in self.kwargs:
            input_dir = os.path.join(input_dir, self.kwargs['obs_dir'])
            # check whether directory exists (if present)
            if not os.path.exists(input_dir):
                wargs = [self.kwargs['obs_dir'], input_dir]
                WLOG(params, 'warning', textentry('10-503-00009', args=wargs))
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
                        wmsg = textentry('10-503-00010', args=wargs)
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
                        wmsg = textentry('10-503-00010', args=wargs)
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
def run_process(params: ParamDict, recipe: DrsRecipe, indexdbm: IndexDatabase,
                module: Any, *gargs, terminate=False, **gkwargs):
    # generate run table (dictionary from reprocessing)
    runtable = generate_run_table(params, module, *gargs, **gkwargs)
    # Generate run list
    rlist = generate_run_list(params, indexdbm, runtable, None)
    # Process run list
    outlist, has_errors, _ = process_run_list(params, recipe, rlist)
    # display errors
    if has_errors:
        # terminate here
        if terminate:
            display_errors(params, outlist)
            eargs = [module.name, recipe.name]
            WLOG(params, 'error', textentry('00-001-00043', args=eargs))
        else:
            eargs = [module.name, recipe.name]
            WLOG(params, 'warning', textentry('00-001-00043', args=eargs))
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
            WLOG(params, 'error', textentry('09-503-00002', args=[runfile]))
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
        WLOG(params, 'error', textentry('09-503-00003', args=eargs))
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
                WLOG(params, 'error', textentry('09-503-00004', args=eargs))
                runid = None
            # check if we already have this column
            if runid in runtable:
                wargs = [runid, keytable[runid], runtable[runid],
                         keys[it], values[it][:40] + '...']
                WLOG(params, 'warning', textentry('10-503-00001', args=wargs))
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
            if key in params:
                # only log if value was not null before
                if not drs_text.null_text(params[key], ['None']):
                    wargs = [key, params[key], value]
                    wmsg = textentry('10-503-00002', args=wargs)
                    WLOG(params, 'warning', wmsg)
            # add to params
            params[key] = value
            params.set_source(key, func_name)
    # ----------------------------------------------------------------------
    # push default values (in case we don't have values in run file
    for key in RUN_KEYS:
        if key not in params:
            # warning that we are using default settings
            wargs = [key, RUN_KEYS[key]]
            WLOG(params, 'warning', textentry('10-503-00005', args=wargs))
            # push keys to params
            params[key] = RUN_KEYS[key]
            params.set_source(key, __NAME__ + '.RUN_KEYS')

    # ----------------------------------------------------------------------
    # deal with arguments from command line (params['INPUTS'])
    # ----------------------------------------------------------------------
    # set observation directory
    if 'OBS_DIR' in params['INPUTS']:
        # get night name
        _obs_dir = params['INPUTS']['OBS_DIR']
        # deal with none nulls
        if not drs_text.null_text(_obs_dir, ['None', '', 'All']):
            params['OBS_DIR'] = _obs_dir
    # make sure observation directory is str or None
    if drs_text.null_text(params['OBS_DIR'], ['None', '', 'All']):
        params['OBS_DIR'] = None
    # ----------------------------------------------------------------------
    # exclude observation directories
    if 'EXCLUDE_OBS_DIRS' in params['INPUTS']:
        # get night name blacklist
        _ex_obs_dirs = params['INPUTS']['EXCLUDE_OBS_DIRS']
        # deal with non-null value
        if not drs_text.null_text(_ex_obs_dirs, ['None', '', 'All']):
            exclude = params['INPUTS'].listp('EXCLUDE_OBS_DIRS')
            params['EXCLUDE_OBS_DIRS'] = exclude
    # ----------------------------------------------------------------------
    # include observation directories
    if 'INCLUDE_OBS_DIRS' in params['INPUTS']:
        # get night name whitelist
        _inc_obs_dirs = params['INPUTS']['INCLUDE_OBS_DIRS']
        # deal with non-null value
        if not drs_text.null_text(_inc_obs_dirs, ['None', '', 'All']):
            include = params['INPUTS'].listp('INCLUDE_OBS_DIRS')
            params['INCLUDE_OBS_DIRS'] = include
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
        if params['OBS_DIR'] is None and params['TRIGGER_RUN']:
            # cause an error if obs_dir not set
            WLOG(params, 'error', textentry('09-503-00010'))
    # ----------------------------------------------------------------------
    # switch for setting science targets (from user inputs)
    if 'SCIENCE_TARGETS' in params['INPUTS']:
        # get the value of science_targets
        _science_targets = params['INPUTS']['SCIENCE_TARGETS']
        # deal with non null value
        if not drs_text.null_text(_science_targets, ['', 'None']):
            # remove leading/trailing speechmarks
            _science_targets = drs_text.cull_leading_trailing(_science_targets,
                                                              ['"', "'"])
            # set science targets
            params['SCIENCE_TARGETS'] = _science_targets
    # ----------------------------------------------------------------------
    # switch for setting telluric target list (from user inputs)
    if 'TELLURIC_TARGETS' in params['INPUTS']:
        # get the value of telluric targets
        _tellu_targets = params['INPUTS']['TELLURIC_TARGETS']
        # deal with non null value
        if not drs_text.null_text(_tellu_targets, ['', 'None']):
            # remove leading/trailing speechmarks
            _tellu_targets = drs_text.cull_leading_trailing(_tellu_targets,
                                                            ['"', "'"])
            # set telluric targets
            params['TELLURIC_TARGETS'] = _tellu_targets
    # ----------------------------------------------------------------------
    # switch whether we update object database (from user inputs)
    if 'UPDATE_OBJDB' in params['INPUTS']:
        # get the value of update obj database from inputs
        _update_objdb = params['INPUTS']['UPDATE_OBJDB']
        # deal with non null values only
        if not drs_text.null_text(_update_objdb, ['', 'None']):
            # get True/False
            _update_objdb = drs_text.true_text(_update_objdb)
            # set value
            params['UPDATE_OBJ_DATABASE'] = _update_objdb
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
    WLOG(params, '', textentry('90-503-00017'))
    # load log database
    logdbm = drs_database.LogDatabase(params)
    logdbm.load_db()
    # deal with white list for directories
    if drs_text.null_text(params['INCLUDE_OBS_DIRS'], ['', 'All', 'None']):
        include_list = None
    else:
        include_list = params['INCLUDE_OBS_DIRS']
    # deal with black list for directories
    if drs_text.null_text(params['EXCLUDE_OBS_DIRS'], ['', 'All', 'None']):
        exclude_list = None
    else:
        exclude_list = params['EXCLUDE_OBS_DIRS']
    # deal with obs_dir set (take precedences over white list)
    if not drs_text.null_text(params['OBS_DIR'], ['', 'None', 'All']):
        include_list = [params['OBS_DIR']]
    # need to remove those that didn't end
    condition = 'ENDED = 1'
    # get runstrings
    table = logdbm.get_entries('RECIPE, RUNSTRING',
                               include_obs_dirs=include_list,
                               exclude_obs_dirs=exclude_list,
                               condition=condition)
    recipes = np.array(table['RECIPE'])
    runstrings = np.array(table['RUNSTRING'])
    arguments = []
    # loop around runstrings
    for runstring in runstrings:
        # clean run string
        clean_runstring = skip_clean_arguments(runstring)
        # append only clean arguments
        arguments.append(clean_runstring.strip())
    # deal with nothing to skip
    if len(recipes) == 0:
        return None
    # push into skip table
    skip_table = Table()
    skip_table['RECIPE'] = recipes
    skip_table['RUNSTRING'] = arguments
    # log number of runs found
    WLOG(params, '', textentry('90-503-00018', args=[len(skip_table)]))
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
    # check whether send email
    if not params['SEND_EMAIL']:
        return 0
    # ----------------------------------------------------------------------
    # try to import yagmail
    try:
        import yagmail
        yag = yagmail.SMTP(params['EMAIL_ADDRESS'])
    except ImportError:
        WLOG(params, 'error', textentry('00-503-00001'))
        yagmail = None
        yag = yagmail
    except Exception as e:
        eargs = [type(e), e, func_name]
        WLOG(params, 'error', textentry('00-503-00002', args=eargs))
        yagmail = None
        yag = yagmail
    # ----------------------------------------------------------------------
    # deal with kind = start
    if kind == 'start':
        receiver = params['EMAIL_ADDRESS']
        iname = '{0}-DRS'.format(params['INSTRUMENT'])
        sargs = [iname, __NAME__, params['PID']]
        subject = textentry('40-503-00001', args=sargs)
        body = ''
        for logmsg in WLOG.pout['LOGGER_ALL']:
            body += '{0}\t{1}\n'.format(*logmsg)
    # ----------------------------------------------------------------------
    # deal with kind = end
    elif kind == 'end':
        receiver = params['EMAIL_ADDRESS']
        iname = '{0}-DRS'.format(params['INSTRUMENT'])
        sargs = [iname, __NAME__, params['PID']]
        subject = textentry('40-503-00002', args=sargs)
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
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Working')
    # check if we need to reset directory
    if params['RESET_TMP']:
        reset = drs_reset.reset_confirmation(params, 'Working',
                                             params['DRS_DATA_WORKING'])
        # reset directory using reset module
        if reset:
            drs_reset.reset_tmp_folders(params, log=True)
        # print that we are not resetting directory
        else:
            WLOG(params, '', textentry('40-502-00013', args=['Tmp']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Reduced')
    # check if we need to reset directory
    if params['RESET_REDUCED']:
        reset = drs_reset.reset_confirmation(params, 'Reduced',
                                             params['DRS_DATA_REDUC'])
        # reset directory using reset module
        if reset:
            drs_reset.reset_reduced_folders(params, log=True)
        # print that we are not resetting directory
        else:
            WLOG(params, '', textentry('40-502-00013', args=['Reduced']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Calibration')
    # check if we need to reset directory
    if params['RESET_CALIB']:
        reset = drs_reset.reset_confirmation(params, 'Calibration',
                                             params['DRS_CALIB_DB'])
        # reset directory using reset module
        if reset:
            drs_reset.reset_calibdb(params, log=True)
        # print that we are not resetting directory
        else:
            WLOG(params, '', textentry('40-502-00013', args=['Calibration']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Telluric')
    # check if we need to reset directory
    if params['RESET_TELLU']:
        reset = drs_reset.reset_confirmation(params, 'Telluric',
                                             params['DRS_TELLU_DB'])
        # reset directory using reset module
        if reset:
            drs_reset.reset_telludb(params, log=True)
        # print that we are not resetting directory
        else:
            WLOG(params, '', textentry('40-502-00013', args=['Telluric']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Log')
    # check if we need to reset directory
    if params['RESET_LOG']:
        # deal with files to skip
        exclude_files = []
        exclude_files.append(drs_log.get_logfilepath(WLOG, params))
        reset = drs_reset.reset_confirmation(params, 'Log',
                                             params['DRS_DATA_MSG'])
        # reset directory using reset module
        if reset:
            drs_reset.reset_log(params, exclude_files)
        # print that we are not resetting directory
        else:
            WLOG(params, '', textentry('40-502-00013', args=['Log']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Plot')
    # check if we need to reset directory
    if params['RESET_PLOT']:
        reset = drs_reset.reset_confirmation(params, 'Plotting',
                                             params['DRS_DATA_PLOT'])
        # reset directory using reset module
        if reset:
            drs_reset.reset_plot(params)
        # print that we are not resetting directory
        else:
            WLOG(params, '', textentry('40-502-00013', args=['Plot']))


def generate_run_list(params, indexdbm: IndexDatabase, runtable,
                      skiptable):
    # print progress: generating run list
    WLOG(params, 'info', textentry('40-503-00011'))
    # need to update table object names to match preprocessing
    #   table can be None if coming from e.g fit_tellu_db

    # get recipe definitions module (for this instrument)
    recipemod = _get_recipe_module(params)
    # get all values (upper case) using map function
    rvalues = _get_rvalues(runtable)
    # check if rvalues has a run sequence
    sequencelist = _check_for_sequences(rvalues, recipemod)
    # set rlist to None (for no sequences)
    rlist = None
    # if we have found sequences need to deal with them
    #   also table cannot be None at this point
    if (sequencelist is not None) and (IndexDatabase is not None):
        # loop around sequences
        for sequence in sequencelist:
            # log progress
            WLOG(params, 'info', textentry('40-503-00009', args=[sequence[0]]))
            # generate new runs for sequence
            newruns = _generate_run_from_sequence(params, sequence,
                                                  indexdbm)
            # update runtable with sequence generation
            runtable, rlist = update_run_table(sequence, runtable, newruns,
                                               rlist)
    # all runtable elements should now be in recipe list
    _check_runtable(params, runtable, recipemod)
    # return Run instances for each runtable element
    return generate_ids(params, indexdbm, runtable, recipemod, skiptable,
                        rlist)


def process_run_list(params, recipe, runlist, group=None):
    # start a timer
    process_start = time.time()
    # get number of cores
    cores = _get_cores(params)
    # pipe to correct module
    # do not use parallelization
    if cores == 1:
        # log process: Running with 1 core
        WLOG(params, 'info', textentry('40-503-00016'))
        # run as linear process
        rdict = _linear_process(params, runlist, group=group)
    # use pool to continue parallelization
    elif params['REPROCESS_MP_TYPE'].lower() == 'pool':
        # log process: Running with N cores
        WLOG(params, 'info', textentry('40-503-00017', args=[cores]))
        # run as multiple processes
        rdict = _multi_process_pool(params, runlist, cores=cores,
                                    groupname=group)
    # use Process to continue parallelization
    else:
        # log process: Running with N cores
        WLOG(params, 'info', textentry('40-503-00017', args=[cores]))
        # run as multiple processes
        rdict = _multi_process_process(params, runlist, cores=cores,
                                       groupname=group)
    # end a timer
    process_end = time.time()
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

    # calculate process time
    process_time = process_end - process_start

    # return the output array (dictionary with priority as key)
    #    values is a parameter dictionary consisting of
    #        RECIPE, NIGHT_NAME, ARGS, ERROR, WARNING, OUTPUTS
    return odict, errors, process_time


def display_timing(params, outlist, ptime):
    # get number of cores
    cores = _get_cores(params)
    # display the timings
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
            WLOG(params, '', textentry('40-503-00020', args=wargs))
            WLOG(params, '', '\t\t{0}'.format(outlist[key]['RUNSTRING']),
                 wrap=False)
            WLOG(params, '', '')
            # add to total time
            tot_time += outlist[key]['TIMING']

    # calculate the speed up factor
    speed_up = tot_time / ptime
    # add total time
    WLOG(params, '', params['DRS_HEADER'])
    WLOG(params, 'info', textentry('40-503-00025', args=[tot_time]))
    WLOG(params, 'info', textentry('40-503-00033', args=[ptime]))
    WLOG(params, 'info', textentry('40-503-00034', args=[speed_up, cores]))
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
            WLOG(params, 'warning', textentry('40-503-00019', args=[key]),
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
            WLOG(params, 'warning', textentry('10-503-00011', args=eargs))
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
    obs_dirs = []
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
        # append obs_dir to list
        obs_dirs.append(rdict['OBS_DIR'])
        # append cores used to list
        coresused.append(rdict['COREUSED'])
        # append cores total
        corestot.append(rdict['CORETOT'])
        # append group
        groups.append(rdict['GROUP'])
    # make into a table
    columns = ['ID', 'RECIPE', 'OBS_DIR', 'CORE_NUM', 'CORE_TOT', 'RUNSTRING']
    values = [priorities, recipenames, obs_dirs, coresused, corestot,
              runlists]
    out_fits_table = drs_table.make_table(params, columns, values)
    # write table
    try:
        drs_table.write_table(params, out_fits_table, out_fits_path)
    except Exception as e:
        eargs = [out_fits_path, type(e), e, func_name]
        WLOG(params, 'warning', textentry('10-503-00012', args=eargs))

    # make txt table
    try:
        with open(out_txt_path, 'w') as f:
            for value in runlists:
                f.write(value + '\n')
    except Exception as e:
        eargs = [out_txt_path, type(e), e, func_name]
        WLOG(params, 'warning', textentry('10-503-00012', args=eargs))


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
                WLOG(params, 'error', textentry('00-503-00010', args=eargs))
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
                WLOG(params, 'error', textentry('00-503-00010', args=eargs))
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
def generate_ids(params, indexdb, runtable, mod, skiptable, rlist=None,
                 **kwargs):
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
    # store skip previous runstrings (so it is not recalculated every time)
    skip_storage = dict()
    # log progress: Validating ids
    WLOG(params, 'info', textentry('40-503-00015', args=[len(runlist)]))
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
        WLOG(params, '', textentry('40-503-00004', args=wargs))
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', textentry('40-503-00013', args=[run_item]))
        # create run object
        run_object = Run(params, indexdb, run_item, mod=mod,
                         priority=keylist[it], inrecipe=input_recipe)
        # deal with input recipe
        if input_recipe is None:
            input_recipe = run_object.recipe
        # deal with skip
        skip, reason = skip_run_object(params, run_object, skiptable,
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
            WLOG(params, '', textentry('40-503-00005', args=wargs))
            # append to run_objects
            run_objects.append(run_object)
        # else log that we are skipping
        else:
            # log that we have skipped run
            wargs = [runid, reason]
            WLOG(params, '', textentry('40-503-00006', args=wargs),
                 colour='yellow')
    # return run objects
    return run_objects


def skip_run_object(params, runobj, skiptable, skip_storage):
    # get recipe and runstring
    recipe = runobj.recipe
    # ----------------------------------------------------------------------
    # check if the user wants to run this runobj (in run list)
    if runobj.runname in params:
        # if user has set the runname to False then we want to skip
        if not params[runobj.runname]:
            return True, textentry('40-503-00007')
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
                return True, textentry('40-503-00032')
            else:
                return False, None
        else:
            # debug log
            dargs = [runobj.skipname]
            WLOG(params, 'debug', textentry('90-503-00004', args=dargs))
            # return False and no reason
            return False, None
    # ----------------------------------------------------------------------
    else:
        # debug log
        dargs = [runobj.skipname]
        WLOG(params, '', textentry('90-503-00005', args=dargs))
        # return False and no reason
        return False, '{0} not present'.format(runobj.skipname)


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


def _generate_run_from_sequence(params, sequence, indexdb: IndexDatabase):
    func_name = __NAME__ + '.generate_run_from_sequence()'
    # -------------------------------------------------------------------------
    # get telluric stars and non-telluric stars
    # -------------------------------------------------------------------------
    # get all telluric stars
    tstars = telluric.get_tellu_include_list(params)
    # get all other stars
    ostars = _get_non_telluric_stars(params, indexdb, tstars)
    # -------------------------------------------------------------------------
    # get odometer reject list (if required)
    # -------------------------------------------------------------------------
    # get whether the user wants to use reject list
    _use_odo_reject = params['USE_ODO_REJECTLIST']
    # get the odometer reject list
    odo_reject_list = []
    if not drs_text.null_text(_use_odo_reject, ['', 'None']):
        if drs_text.true_text(_use_odo_reject):
            odo_reject_list = gen_pp.get_reject_list(params)
    # -------------------------------------------------------------------------
    # get template list (if required)
    # -------------------------------------------------------------------------
    # get whether to recalculate templates
    _recal_templates = params['RECAL_TEMPLATES']
    # get a list of object names with templates
    template_object_list = []
    if not drs_text.null_text(_recal_templates, ['', 'None']):
        if not drs_text.true_text(_recal_templates):
            template_object_list = telluric.list_current_templates(params)
    # -------------------------------------------------------------------------
    # get filemod and recipe mod
    pconst = constants.pload()
    filemod = pconst.FILEMOD()
    recipemod = pconst.RECIPEMOD()
    # generate sequence
    sequence[1].process_adds(params, tstars=list(tstars), ostars=list(ostars),
                             template_stars=template_object_list)
    # get the sequence recipe list
    srecipelist = sequence[1].sequence
    # storage for new runs to add
    newruns = []
    # define the master conditions (that affect all recipes)
    master_condition = gen_global_condition(params, indexdb,
                                            odo_reject_list)
    # ------------------------------------------------------------------
    # check we have rows left
    # ------------------------------------------------------------------
    # get length of database at this point
    idb_len = indexdb.database.count(indexdb.database.tname,
                                     condition=master_condition)
    # deal with empty database (after conditions)
    if idb_len == 0:
        eargs = [master_condition, func_name]
        WLOG(params, 'error', textentry('00-503-00018', args=eargs))
        # get response for how to continue (skip or exit)
        response = prompt(params)
        if not response:
            sys.exit()
    # log that we are processing recipes
    WLOG(params, 'info', textentry('40-503-00037', args=[idb_len]))
    # ------------------------------------------------------------------
    # loop around recipes in new list
    for srecipe in srecipelist:
        # deal with skip
        runname = 'RUN_{0}'.format(srecipe.shortname)
        # skip if runname is not True
        if runname in params:
            if not params[runname]:
                wargs = [srecipe.name, srecipe.shortname]
                WLOG(params, '', textentry('40-503-00021', args=wargs),
                     colour='yellow')
                continue
        # print progress
        wargs = [srecipe.name, srecipe.shortname]
        WLOG(params, '', textentry('40-503-00012', args=wargs))
        # add file and recipe mod if not set
        if srecipe.recipemod is None:
            srecipe.recipemod = recipemod.copy()
        if srecipe.filemod is None:
            srecipe.filemod = filemod.copy()
        # add params to srecipe
        srecipe.params = params
        # copy master condition
        condition = str(master_condition)
        # ------------------------------------------------------------------
        # Deal with no rows in table
        # ------------------------------------------------------------------
        # get length of database at this point
        idb_len = indexdb.database.count(indexdb.database.tname,
                                         condition=condition)
        # skip if table is empty
        if idb_len == 0:
            continue
        # ------------------------------------------------------------------
        # Deal with recalculation of templates
        # ------------------------------------------------------------------
        # only do this for recipes with flag "template_required"
        if srecipe.template_required:
            # only continue if we have objects with templates
            if len(template_object_list) > 0:
                # store sub-conditions
                subs = []
                # add to global conditions
                for objname in template_object_list:
                    # build sub-condition
                    subs += ['KW_OBJNAME="{0}"'.format(objname)]
                # generate full subcondition
                subcondition = ' OR '.join(subs)
                # add to global condition (in reverse - we don't want these)
                condition += ' AND NOT ({0})'.format(subcondition)
        # ------------------------------------------------------------------
        # deal with directory filters (master observation directory and
        # obs_dir filter)
        # ------------------------------------------------------------------
        # master observation directory
        # ------------------------------------------------------------------
        if srecipe.master:
            # get master observation directory
            obs_dir = params['MASTER_OBS_DIR']
            # get observation directory
            obs_dirs = indexdb.database.unique('OBS_DIR', condition=condition,
                                               table=indexdb.database.tname)
            # check if master observation directory is valid (in table)
            if obs_dir not in obs_dirs:
                wargs = [obs_dir]
                WLOG(params, 'warning', textentry('10-503-00004', args=wargs))
                # get response for how to continue (skip or exit)
                response = prompt(params)
                if response:
                    continue
                else:
                    sys.exit()
            # mask table by observation directory
            condition += ' AND OBS_DIR="{0}"'.format(obs_dir)
        # ------------------------------------------------------------------
        # deal with setting 1 night
        # ------------------------------------------------------------------
        elif not drs_text.null_text(params['OBS_DIR'], ['', 'All', 'None']):
            # get observation directory
            obs_dir = params['OBS_DIR']
            # mask table by observation directory
            condition += ' AND OBS_DIR="{0}"'.format(obs_dir)
        else:
            obs_dir = 'all'
        # ------------------------------------------------------------------
        # get length of database at this point
        idb_len = indexdb.database.count(indexdb.database.tname,
                                         condition=condition)
        # deal with empty database (after conditions)
        if idb_len == 0:
            wargs = [obs_dir]
            WLOG(params, 'warning', textentry('10-503-00003', args=wargs))
            # get response for how to continue (skip or exit)
            response = prompt(params)
            if response:
                continue
            else:
                sys.exit()
        # ------------------------------------------------------------------
        # deal with filters defined in recipe
        # ------------------------------------------------------------------
        filters = _get_filters(params, srecipe)
        # get fiber filter
        allowedfibers = srecipe.allowedfibers
        # ------------------------------------------------------------------
        # get runs for this recipe
        # ------------------------------------------------------------------
        sruns = generate_runs(params, srecipe, indexdb, condition=condition,
                              filters=filters,
                              allowedfibers=allowedfibers)
        # ------------------------------------------------------------------
        # print how many runs we are adding
        # ------------------------------------------------------------------
        # TODO: move to language database
        WLOG(params, '', '\t\tAdded {0} runs'.format(len(sruns)))
        # ------------------------------------------------------------------
        # deal with trigger and no runs left to do
        # ------------------------------------------------------------------
        # if we are in trigger mode we need to stop when we have no
        #   sruns for recipe
        if params['INPUTS']['TRIGGER'] and len(sruns) == 0:
            # display message that we stopped here as no files were found
            wargs = [srecipe.name]
            WLOG(params, 'info', textentry('40-503-00028', args=wargs))
            # stop processing recipes
            break
        # ------------------------------------------------------------------
        # append runs to output list
        # ------------------------------------------------------------------
        # append runs to new runs list
        for srun in sruns:
            newruns.append([srun, srecipe])
    # return all new runs
    return newruns


def generate_runs(params: ParamDict, recipe: DrsRecipe,
                  indexdb: IndexDatabase, condition: str,
                  filters: Union[Dict[str, Any], None] = None,
                  allowedfibers: Union[List[str], str, None] = None
                  ) -> List[str]:
    """
    Generate a list of run strings from a table of raw files given a set of
    filters for this DrsRecipe (i.e. use args/keywords from recipe
    definition)

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe instance, the recipe this run is associated with
    :param indexdb: index database instance, the file database to use to
                    generate runs
    :param condition: str, the condition to apply to the database
    :param filters: None or dict - dictionary of filters where keys are
                    KW_XXX names (in params) and values are the values to
                    test in the header(s)
    :param allowedfibers: list of strings, the list if fibers that are
                          allowed for this generation

    :return: list of strings, the runs (as if recipes run from the command
             line
    """
    # set function name
    _ = display_func('generate_runs', __NAME__)
    # need to find files in index database that match each argument
    #    filedict is a dictionary of arguments each for
    #    each drsfile (if filelogic=exclusive)
    #       i.e. filedict[argname][drsfile]
    #    else all drsfiles go to 'all'
    #       i.e. filedict[argname]['all']
    argdict = find_run_files(params, recipe, indexdb, condition, recipe.args,
                             filters=filters, allowedfibers=allowedfibers)
    # same for keyword args but this time we need to check only if
    #   keyword is required, else skip (don't add optionals)
    kwargdict = find_run_files(params, recipe, indexdb, condition,
                               recipe.kwargs, filters=filters,
                               allowedfibers=allowedfibers,
                               check_required=True)
    # now we have the file lists we need to group files and match where
    #   there are more than one argument, we then add in the other
    #   arguments and construct the runs
    runargs = group_run_files2(params, recipe, argdict, kwargdict)
    # now we have the runargs we can convert to a runlist
    runlist = convert_to_command(params, recipe, runargs)
    # clear printer
    drs_log.Printer(None, None, '')
    # return the runlist
    return runlist


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
    # prompt the user for response
    uinput = input(textentry(('40-503-00022')))
    # get the True/False responses
    true = textentry('40-503-00023')
    false = textentry('40-503-00024')

    if true.upper() in uinput.upper():
        return 1
    elif false.upper() in uinput.upper():
        return 0
    else:
        return 1


def gen_global_condition(params: ParamDict, indexdb: IndexDatabase,
                         odo_reject_list: List[str]) -> str:
    """
    Generate the global conditions (based on run.ini) that will affect the
    sql conditions on all recipes i.e.:
    - filtering engineering nights
    - filtering rejected nights
    - filtering accepted nights
    - filtering pi names
    - filtering rejected odometer codes

    :param params: ParamDict, the parameter dictionary of constants
    :param indexdb: IndexDatabase instance, the index database instance
    :param odo_reject_list: list or strings, the list of rejected odometer
                            codes
    :return: str, the sql global condition to apply to all recipes
    """
    # set up an sql condition that will get more complex as we go down
    condition = 'BLOCK_KIND="raw"'
    # ------------------------------------------------------------------
    # filer out engineering directories
    # ------------------------------------------------------------------
    if not params['ENGINEERING']:
        # log that we are checking engineering nights
        WLOG(params, '', textentry('40-503-00035'))
        # get sub condition for engineering nights
        subcondition = _remove_engineering(params, indexdb, condition)
        # add to conditions
        condition += subcondition
        # get length of database at this point
        idb_len = indexdb.database.count(indexdb.database.tname,
                                         condition=condition)
        # deal with empty database (after conditions)
        if idb_len == 0:
            WLOG(params, 'warning', textentry('10-503-00016'))
            # get response for how to continue (skip or exit)
            response = prompt(params)
            if response:
                pass
            else:
                sys.exit()
    # ------------------------------------------------------------------
    # deal with black lists
    # ------------------------------------------------------------------
    # black list
    if not drs_text.null_text(params['EXCLUDE_OBS_DIRS'], ['', 'All', 'None']):
        # get black list from params
        exclude_obs_dirs = params.listp('EXCLUDE_OBS_DIRS', dtype=str)
        # loop around blacklist
        for exclude_obs_dir in exclude_obs_dirs:
            # add to condition
            condition += ' AND (OBS_DIR!="{0}")'.format(exclude_obs_dir)
        # log blacklist
        wargs = [' ,'.join(exclude_obs_dirs)]
        WLOG(params, '', textentry('40-503-00026', args=wargs))
        # get length of database at this point
        idb_len = indexdb.database.count(indexdb.database.tname,
                                         condition=condition)
        # deal with empty database (after conditions)
        if idb_len == 0:
            WLOG(params, 'warning', textentry('10-503-00006'))
            # get response for how to continue (skip or exit)
            response = prompt(params)
            if response:
                pass
            else:
                sys.exit()
    # ------------------------------------------------------------------
    # deal with white list
    # ------------------------------------------------------------------
    if not drs_text.null_text(params['INCLUDE_OBS_DIRS'], ['', 'All', 'None']):
        # get white list from params
        whitelist_nights = params.listp('INCLUDE_OBS_DIRS', dtype=str)
        # define a subcondition
        subconditions = []
        # loop around white listed nights and set them to False
        for whitelist_night in whitelist_nights:
            # add subcondition
            subcondition = 'OBS_DIR="{0}"'.format(whitelist_night)
            subconditions.append(subcondition)
        # add to conditions
        condition += ' AND ({0})'.format(' OR '.join(subconditions))
        # log whitelist
        wargs = [' ,'.join(whitelist_nights)]
        WLOG(params, '', textentry('40-503-00027', args=wargs))
        # get length of database at this point
        idb_len = indexdb.database.count(indexdb.database.tname,
                                         condition=condition)
        # deal with empty database (after conditions)
        if idb_len == 0:
            WLOG(params, 'warning', textentry('10-503-00007'))
            # get response for how to continue (skip or exit)
            response = prompt(params)
            if response:
                pass
            else:
                sys.exit()
    # ------------------------------------------------------------------
    # deal with pi name filter
    # ------------------------------------------------------------------
    if not drs_text.null_text(params['PI_NAMES'], ['', 'All', 'None']):
        # get pi name list from params
        pi_names = params.listp('PI_NAMES', dtype=str)
        # define a subcondition
        subconditions = []
        # loop around pi names and set them to False
        for pi_name in pi_names:
            # add subcondition
            subcondition = 'KW_PI_NAME="{0}"'.format(pi_name)
            subconditions.append(subcondition)
        # add to conditions
        condition += ' AND ({0})'.format(' OR '.join(subconditions))
        # log pi name
        wargs = [' ,'.join(pi_names)]
        WLOG(params, '', textentry('40-503-00029', args=wargs))
        # get length of database at this point
        idb_len = indexdb.database.count(indexdb.database.tname,
                                         condition=condition)
        # deal with empty database (after conditions)
        if idb_len == 0:
            WLOG(params, 'warning', textentry('10-503-00015'))
            # get response for how to continue (skip or exit)
            response = prompt(params)
            if response:
                pass
            else:
                sys.exit()
    # ------------------------------------------------------------------
    # Deal with odometer reject list
    # ------------------------------------------------------------------
    # only continue if we have odocodes to reject
    if len(odo_reject_list) > 0:
        # log progress
        WLOG(params, '', textentry('40-503-00036'))
        # store sub-conditions
        subs = []
        # add to global conditions
        for odocode in odo_reject_list:
            # get fkwargs
            fkwargs = dict(odocode=odocode)
            # build sub-condition
            subs += ['FILENAME LIKE "{odocode}%.fits"'.format(**fkwargs)]
        # generate full subcondition
        subcondition = ' OR '.join(subs)
        # add to global condition (in reverse - we don't want these)
        condition += ' AND NOT ({0})'.format(subcondition)
    # ------------------------------------------------------------------
    # Return global condition
    # ------------------------------------------------------------------
    # return the condition
    return condition


# =============================================================================
# Define processing functions
# =============================================================================
def _linear_process(params, runlist, number=0, cores=1, event=None,
                    group=None, return_dict=None, ):
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
        pp['OBS_DIR'] = str(run_item.obs_dir)
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
                # plotter = plotting.Plotter(params, recipe)
                # plotter.closeall()
                close_all_plots()
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
                emsgs = [textentry('00-503-00005', args=[priority])]
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
                emsgs = [textentry('00-503-00004', args=[priority])]
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
                emsgs = [textentry('00-503-00015', args=[priority])]
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
                WLOG(params, 'debug', textentry('90-503-00008', args=wargs))
                event.set()
        # ------------------------------------------------------------------
        # append to return dict
        return_dict[priority] = pp
    # return the output array
    return return_dict


def _multi_process_process(params, runlist, cores, groupname=None):
    # first try to group tasks
    grouplist, groupnames = _group_tasks1(runlist, cores)
    # import multiprocessing
    from multiprocessing import Process, Manager, Event
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
            args = [params, runlist_group, r_it + 1,
                    cores, event, groupname, return_dict]
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


def _multi_process_pool(params, runlist, cores, groupname=None):
    # first try to group tasks (now just by recipe)
    grouplist, groupnames = _group_tasks2(runlist, cores)
    # deal with Pool specific imports
    from multiprocessing import Manager
    from multiprocessing import get_context
    from multiprocessing import set_start_method
    try:
        set_start_method("spawn")
    except RuntimeError:
        pass
    # start process manager
    manager = Manager()
    event = manager.Event()
    return_dict = dict()

    # loop around groups
    #   - each group is a unique recipe
    for g_it, groupnum in enumerate(grouplist):
        # get this groups values
        group = grouplist[groupnum]
        # log progress
        _group_progress(params, g_it, grouplist, groupnames[groupnum])
        # skip groups if event is set
        if event is not None and event.is_set():
            # TODO: Add to language db
            WLOG(params, 'warning', '\tSkipping group')
            continue
        # list of params for each entry
        params_per_process = []
        # populate params for each sub group
        for r_it, runlist_group in enumerate(group):
            args = [params, [runlist_group], r_it + 1,
                    cores, event, groupname]
            params_per_process.append(args)
        # start parellel jobs
        with get_context('spawn').Pool(cores, maxtasksperchild=1) as pool:
            results = pool.starmap(_linear_process, params_per_process)
        # fudge back into return dictionary
        for row in range(len(results)):
            for key in results[row]:
                return_dict[key] = results[row][key]

    # return return_dict
    return dict(return_dict)


def close_all_plots():
    """
    Close all plots (by importing matplotlib)

    :return:
    """
    global PLT_MOD
    if PLT_MOD is not None:
        PLT_MOD.close('all')
        return
    else:
        from apero.plotting.core import import_matplotlib
        out = import_matplotlib()
        if out is not None:
            plt = out[0]
            plt.close('all')
            PLT_MOD = plt


# =============================================================================
# Define run making functions
# =============================================================================
# define complex type argdict
ArgDictType = Union[Dict[str, Table], OrderedDict, None]


def find_run_files(params: ParamDict, recipe: DrsRecipe,
                   indexdb: IndexDatabase, condition: str,
                   args: Dict[str, DrsArgument],
                   filters: Union[Dict[str, Any], None] = None,
                   allowedfibers: Union[List[str], str, None] = None,
                   check_required: bool = False) -> Dict[str, ArgDictType]:
    """
    Given a specifc recipe and args (args or kwargs) use the other arguments
    to generate a set of astropy.table.Table for each arg (args or kwargs)
    - it does this via checking the full 'table' against all filters etc
    and returns (for each arg/kwargs)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe for which to find files (uses some
                   properties (i.e. extras and master) already set previously
    :param indexdb: index database instance, the file database to use to
                    generate runs
    :param condition: str, the condition to apply to the database
    :param args: dict, either args or kwargs - the DrsRecipe.args or
                 DrsRecipe.kwargs to use - produces a table for each key in
                 this dict
    :param filters: dict, the keys to check (should be KW_XXX) and should also
                    be columns in 'table'
    :param allowedfibers: str, the allowed fiber(s) (should be in KW_FIBER
                          column in 'table'
    :param absfile_col: str, the absolute file column name (if not set is taken
                        from params['REPROCESS_ABSFILECOL'] - recommended
    :param check_required: bool, if True checks whether parameter is required
                           (set in argument definition - in recipe definition)

    :return: a dictionary for each 'arg' key, each dictionary has a
             sub-dictionary for each unique drsfile type found (the value of
             the sub-dictionary is an astropy.table - a sub-set of the full
             table matching this argument/drsfile combination
    """
    # set function name
    func_name = display_func('find_run_files', __NAME__)
    # storage for valid files for each argument
    filedict = OrderedDict()
    # copy condition
    master_condtion = str(condition)
    # get valid database column names
    index_colnames = indexdb.database.colnames('*', indexdb.database.tname)
    # debug log the number of files found
    idb_len = indexdb.database.count(indexdb.database.tname,
                                     condition=condition)
    dargs = [func_name, idb_len]
    WLOG(params, 'debug', textentry('90-503-00011', args=dargs))
    # loop around arguments
    for argname in args:
        # get arg instance
        arg = args[argname]
        # if check required see if parameter is required
        if check_required:
            if not arg.required and not arg.reprocess:
                continue
        # see if we are over writing argument
        if argname in recipe.extras:
            filedict[argname] = recipe.extras[argname]
            continue
        # make sure we are only dealing with dtype=files
        if arg.dtype not in ['file', 'files']:
            # deal with any special non file arguments
            filedict = add_non_file_args(params, recipe, argname, arg,
                                         filedict)
            continue
        # add sub-dictionary for each drs file
        filedict[argname] = OrderedDict()
        # debug log: the argument being scanned
        WLOG(params, 'debug', textentry('90-503-00012', args=[argname]))
        # get drs file instances
        drsfiles = arg.files
        # if files are None continue
        if drsfiles is None:
            continue
        # ------------------------------------------------------------------
        # copy the condition string for this argument
        argcondition = str(master_condtion)
        # loop around filters
        for tfilter in filters:
            # check if filter is valid
            if tfilter in index_colnames:
                # -------------------------------------------------------------
                # deal with filter values being list/str
                if isinstance(filters[tfilter], str):
                    testvalues = [filters[tfilter]]
                elif isinstance(filters[tfilter], list):
                    testvalues = filters[tfilter]
                else:
                    continue
                # -------------------------------------------------------------
                # have multiple values to test --> store these
                sub_cond = []
                # loop around test values with OR (could be any value)
                for testvalue in testvalues:
                    # check if value is string
                    if isinstance(testvalue, str):
                        testvalue = testvalue.strip().upper()
                    # construct sub condition based on this filter
                    sargs = [tfilter, testvalue]
                    sub_cond += ['({0}="{1}")'.format(*sargs)]
                # create  full sub condition (with OR)
                subcondition = ' OR '.join(sub_cond)
                # -------------------------------------------------------------
                # add filter to argument condition
                argcondition += ' AND ({0})'.format(subcondition)
        # ------------------------------------------------------------------
        # lets apply the filters here
        dataframe = indexdb.get_entries('*', condition=argcondition)
        absfilenames = np.array(dataframe['ABSPATH']).astype(str)

        # ------------------------------------------------------------------
        # Now we need to get the files and assign
        #     - infile
        #     - outfile
        #  and deal with exclusivity
        # ------------------------------------------------------------------
        # loop around drs files
        for drsfile in drsfiles:
            # copy dataframe into table
            ftable = Table.from_pandas(dataframe)
            # set params for drsfile
            drsfile.params = params
            # debug log: the file being tested
            dargs = [drsfile.name]
            WLOG(params, 'debug', textentry('90-503-00013', args=dargs))
            # define storage (if not already defined)
            cond1 = drsfile.name not in filedict[argname]
            if cond1 and (arg.filelogic == 'exclusive'):
                filedict[argname][drsfile.name] = []
            elif 'all' not in filedict[argname]:
                filedict[argname]['all'] = []
            # list of valid files
            valid_infiles = []
            valid_outfiles = []
            valid_num = 0
            # loop around files
            for f_it, filename in enumerate(absfilenames):
                # print statement
                pargs = [drsfile.name, f_it + 1, len(absfilenames)]
                pmsg = '\t\tProcessing {0} file {1}/{2}'.format(*pargs)
                drs_log.Printer(None, None, pmsg)
                # get infile instance (i.e. raw or pp file) and assign the
                #   correct outfile (from filename)
                out = drsfile.get_infile_outfilename(recipe.name,
                                                     filename, allowedfibers)
                infile, valid, outfilename = out
                # if still valid add to list
                if valid:
                    valid_infiles.append(infile)
                    valid_outfiles.append(outfilename)
                    valid_num += 1
                else:
                    valid_infiles.append(None)
                    valid_outfiles.append(None)
            # debug log the number of valid files
            WLOG(params, 'debug', textentry('90-503-00014', args=[valid_num]))
            # add outfiles to table
            ftable['OUT'] = valid_outfiles
            # for the valid files we can now check infile headers
            for it in range(len(ftable)):
                # get infile
                infile = valid_infiles[it]
                # skip those that were invalid
                if infile is None:
                    continue
                # else make sure params is set
                else:
                    infile.params = params
                # get table dictionary
                tabledict = dict(zip(ftable.colnames, ftable[it]))
                # check whether tabledict means that file is valid for this
                #   infile
                valid1 = infile.check_table_keys(tabledict)
                # do not continue if valid1 not True
                if not valid1:
                    continue
                # check whether filters are found
                valid2 = infile.check_table_keys(tabledict, rkeys=filters)
                # do not continue if valid2 not True
                if not valid2:
                    continue
                # if valid then add to filedict for this argnameand drs file
                if arg.filelogic == 'exclusive':
                    filedict[argname][drsfile.name].append(ftable[it])
                else:
                    filedict[argname]['all'].append(ftable[it])
    outfiledict = OrderedDict()
    # convert each appended table to a single table per file
    for argname in filedict:
        # deal with non-list arguments
        if not isinstance(filedict[argname], OrderedDict):
            outfiledict[argname] = filedict[argname]
            continue
        else:
            # add sub dictionary
            outfiledict[argname] = OrderedDict()
        # loop around drs files
        for name in filedict[argname]:
            # get table list
            tablelist = filedict[argname][name]
            # deal with combining tablelist
            with warnings.catch_warnings(record=True) as _:
                outfiledict[argname][name] = vstack_cols(params, tablelist)
    # return filedict
    return outfiledict


def add_non_file_args(params: ParamDict, recipe: DrsRecipe,
                      argname: str, arg: DrsArgument,
                      filedict: OrderedDict) -> OrderedDict:
    """
    deal with any non file arguments that have to be treated in a special way

    Currently this includes:

    - directory (when recipe is a master) - muset set to master observation
      directory
    - include_obs_dirs - must push through from processing
    - exclude_obs_dirs - must push through from processing
    - obs_dir - must push through from processing

    - all other arguments user their default value

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the input recipe this was called from
    :param argname: str, the name of the argument we are dealing with
    :param arg: DrsArgument, the argument instance we are dealing with
    :param filedict: OrderedDict, the dictionary for storing all args/kwargs
                     (table for files, constant otherwise)
    :return: OrderedDict, the updated filedict
    """
    # deal with directory (special argument) - if we have a
    #   master observation directory use as the directory name
    if arg.dtype == 'obs_dir' and recipe.master:
        filedict[argname] = params['MASTER_OBS_DIR']
    # need to add directory and set it to None
    elif arg.dtype == 'obs_dir':
        filedict[argname] = None
    # -------------------------------------------------------------------------
    # deal with include observation directory list
    if argname in ['include_obs_dirs']:
        if 'INCLUDE_OBS_DIRS' in params['INPUTS']:
            # get white night list as a string
            include_obs_dirs = params['INPUTS']['INCLUDE_OBS_DIRS']
            # test for null values
            if not drs_text.null_text(include_obs_dirs, ['None', 'All', '']):
                # get white night list as a list
                include_obs_dirs = params['INPUTS'].listp('INCLUDE_OBS_DIRS')
                # add to file dict
                filedict[argname] = include_obs_dirs
    # -------------------------------------------------------------------------
    # deal with exclude observation directory list
    if argname in ['exclude_obs_dirs']:
        if 'EXCLUDE_OBS_DIRS' in params['INPUTS']:
            # get black night list as a string
            exclude_obs_dirs = params['INPUTS']['EXCLUDE_OBS_DIRS']
            # test for null values
            if not drs_text.null_text(exclude_obs_dirs, ['None', 'All', '']):
                # get white night list as a list
                exclude_obs_dirs = params['INPUTS'].listp('EXCLUDE_OBS_DIRS')
                # add to file dict
                filedict[argname] = exclude_obs_dirs
    # -------------------------------------------------------------------------
    # deal with obs directory
    if argname in ['obs_dir']:
        if 'OBS_DIR' in params['INPUTS']:
            # get black night list as a string
            obs_dir = params['INPUTS']['OBS_DIR']
            # test for null values
            if not drs_text.null_text(obs_dir, ['None', 'All', '']):
                # get white night list as a list
                obs_dir = params['INPUTS'].listp('OBS_DIR')
                # add to file dict
                filedict[argname] = obs_dir
    # -------------------------------------------------------------------------
    # else set the file dict value to the default value
    # TODO: Need a better option for this!!
    # TODO:   i.e. when we need values to be set from the header
    elif not drs_text.null_text(arg.default, ['None', 'All', '']):
        filedict[argname] = arg.default
    # return the file dictionary
    return filedict


def group_run_files(params: ParamDict, recipe: DrsRecipe,
                    argdict: Dict[str, ArgDictType],
                    kwargdict: Dict[str, ArgDictType],
                    obs_dir_col: Union[str, None] = None,
                    ) -> List[Dict[str, Any]]:
    """
    Take the arg and kwarg dictionary of tables (argdict and kwargdict) and
    force them into groups (based on sequence number and number in sequence)
    for each positional/optional argument. Then take these sets of files
    and push them into recipe runs (one set of files for each recipe run)
    return is a list of these runs where each 'run' is a dictionary of
    arguments each with the values that specific argument should have

    i.e. cal_extract should have at least ['directory', 'files']

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe these args/kwargs are associated with
    :param argdict: dict, a dictionary of dictionaries containing a table of
                    files each - top level key is a positional argument for this
                    recipe and sub-dict key is a DrsFitsFile instance i.e.:
                    argdict[argument][drsfile] = Table
    :param kwargdict: dict, a dictionary of dictionaries containing a table of
                    files each - top level key is an optional argument for this
                    recipe and sub-dict key is a DrsFitsFile instance i.e.:
                    kwargdict[argument][drsfile] = Table
    :param obs_dir_col: str or None, if set overrides
                         params['REPROCESS_OBSDIR_COL']

    :return: a list of dictionaries, each dictionary is a different run.
             each 'run' is a dictionary of arguments each with the values that
             specific argument should have
    """
    # set function name
    func_name = display_func('group_run_files', __NAME__)
    # get parameters from params
    obs_dir_col = pcheck(params, 'REPROCESS_OBSDIR_COL', func=func_name,
                         override=obs_dir_col)
    # flag for having no file arguments
    has_file_args = False
    # ----------------------------------------------------------------------
    # first loop around arguments
    for argname in argdict:
        # get this arg
        arg = argdict[argname]
        # deal with other parameters (not 'files' or 'file')
        if recipe.args[argname].dtype not in ['file', 'files']:
            continue
        # flag that we have found a file argument
        has_file_args = True
        # get file limit
        limit = recipe.args[argname].limit
        # deal with files (should be in drs groups)
        for name in argdict[argname]:
            # check for None
            if arg[name] is None:
                continue
            # copy row as table
            intable = Table(arg[name])
            # assign individual group numbers / mean group date
            gargs = [params, intable]
            argdict[argname][name] = _group_drs_files(*gargs, limit=limit)
    # ----------------------------------------------------------------------
    # second loop around keyword arguments
    for kwargname in kwargdict:
        # get this kwarg
        kwarg = kwargdict[kwargname]
        # deal with other parameters (not 'files' or 'file')
        if recipe.kwargs[kwargname].dtype not in ['file', 'files']:
            continue
        # flag that we have found a file argument
        has_file_args = True
        # get file limit
        limit = recipe.kwargs[kwargname].limit
        # deal with files (should be in drs groups)
        for name in kwargdict[kwargname]:
            # check for None
            if kwarg[name] is None:
                continue
            # copy row as table
            intable = Table(kwarg[name])
            # assign individual group numbers / mean group date
            gargs = [params, intable]
            kwargdict[kwargname][name] = _group_drs_files(*gargs, limit=limit)
    # ----------------------------------------------------------------------
    # figure out arg/kwarg order
    runorder, rundict = _get_argposorder(recipe, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # brute force approach
    runs = []
    # ----------------------------------------------------------------------
    # deal with no file found (only if we expect to have files)
    if has_file_args:
        all_none = False
        for runarg in runorder:
            # need to check required criteria
            if runarg in recipe.args:
                required = recipe.args[runarg].required
                dtype = recipe.args[runarg].dtype
            else:
                required = recipe.kwargs[runarg].required
                dtype = recipe.kwargs[runarg].dtype
            # only check if file is required and argument is a file type
            if required and dtype in ['file', 'files']:
                # if whole dict is None then all_none is True
                if rundict[runarg] is None:
                    all_none = True
                # if we have entries we have to check each of them
                else:
                    # test this run arg
                    entry_none = False
                    # loop around entries
                    for entry in rundict[runarg]:
                        # if entry is None --> entry None is True
                        if rundict[runarg][entry] is None:
                            entry_none |= True
                    # if entry_none is True then all_none is True
                    if entry_none:
                        all_none = True
        # if all none is True then return no runs
        if all_none:
            return []
    # ----------------------------------------------------------------------
    # find first file argument
    fout = _find_first_filearg(params, runorder, argdict, kwargdict)
    # if fout is None means we have no file arguments
    if fout is None:
        # get new run
        new_runs = _gen_run(params, rundict=rundict, runorder=runorder,
                            masternight=recipe.master)
        # finally add new_run to runs
        runs += new_runs
    else:
        arg0, drsfiles0 = fout
        # ----------------------------------------------------------------------
        # loop around drs files in first file argument
        for drsfilekey in drsfiles0:
            # condition to stop trying to match files
            cond = True
            # set used groups
            usedgroups = dict()
            # get drs table
            drstable = rundict[arg0][drsfilekey]
            # get group column from drstable
            groups = np.array(drstable['GROUPS']).astype(int)
            # get unique groups from groups
            ugroups = np.sort(np.unique(groups))
            # keep matching until condition met
            while cond:
                # print statement
                pmsg = '\t\tProcessing run {0}'.format(len(runs))
                drs_log.Printer(None, None, pmsg)
                # check for None
                if rundict[arg0][drsfilekey] is None:
                    break
                # get first group
                nargs = [arg0, drstable, usedgroups, groups, ugroups]
                gtable0, usedgroups = _find_next_group(*nargs)
                # check for grouptable unset --> skip
                if gtable0 is None:
                    break
                # get observation directory for group
                obs_dir = gtable0[obs_dir_col][0]
                # get mean time for group
                meantime = gtable0['MEANDATE'][0]
                # _match_groups raises exception when finished so need a
                #   try/except here to catch it
                try:
                    new_runs = _gen_run(params, rundict, runorder, obs_dir,
                                        meantime, arg0, gtable0,
                                        master_obs_dir=recipe.master)
                # catch exception
                except DrsRecipeException:
                    continue
                # finally add new_run to runs
                runs += new_runs
    # deal with master (should only be 1)
    if recipe.master:
        return [runs[0]]
    else:
        # return runs
        return runs


def group_run_files2(params: ParamDict, recipe: DrsRecipe,
                     argdict: Dict[str, ArgDictType],
                     kwargdict: Dict[str, ArgDictType]) -> List[Dict[str, Any]]:
    """
    Group run files (using group_function)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe instance, the recipe this group is for
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)

    :return:
    """
    # get grouping function
    group_function = recipe.group_func
    # deal with master
    if recipe.master:
        master = params['MASTER_OBS_DIR']
    else:
        master = None
    # get grouping column
    group_column = recipe.group_column
    if group_column in params:
        group_column = params[group_column]
    # if we have a group function used it
    if group_function is not None:
        # use the group function to generate runs
        return group_function(recipe.args, recipe.kwargs,
                              argdict, kwargdict,
                              group_column=group_column,
                              master=master)
    # if we don't have one give warning
    else:
        # TODO: move to language database
        wmsg = '\tNo runs produced for {0} - No group function given'
        WLOG(params, 'warning', wmsg.format(recipe.shortname))
        return []


def convert_to_command(params: ParamDict, recipe: DrsRecipe,
                       runargs: List[Dict[str, Any]]) -> List[str]:
    """
    Converts our list of dictionaries (for each run) to a list of strings,
    each string representing what would be entered on the command line

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe instance this is for
    :param runargs: a list of dictionaries, each dictionary is a different run.
                    each 'run' is a dictionary of arguments each with the
                    values that specific argument should have
    :return: list of strings, each string representing what would be entered
             on the command line
    """
    # set function name
    _ = display_func('convert_to_command', __NAME__)
    # get args/kwargs from recipe
    args = recipe.args
    kwargs = recipe.kwargs
    # define storage
    outputs = []
    # loop around arguement
    for runarg in runargs:
        # command first arg
        command = '{0} '.format(recipe.name)
        # get run order
        runorder, _ = _get_argposorder(recipe, runarg, runarg)
        # loop around run order
        for argname in runorder:
            # get raw value
            rawvalue = runarg[argname]
            # deal with lists
            if isinstance(rawvalue, list):
                value = ' '.join(runarg[argname])
            else:
                value = str(rawvalue)
            # deal with arguments
            if argname in args:
                # add to command
                command += '{0} '.format(value)
            # deal with keyword arguments
            if argname in kwargs:
                # add to command
                command += '--{0} {1} '.format(argname, value)
        # append to out (removing trailing white spaces)
        outputs.append(command.strip())
    # return outputs
    return outputs


def vstack_cols(params: ParamDict, tablelist: List[Table]
                ) -> Union[Table, None]:
    """
    Take a list of Astropy Tables and stack into single Astropy Table
    Note same as io.drs_table.vstack_cols

    :param params: ParamDict, the parameter dictionary of constants
    :param tablelist: a list of astropy.table.Table to stack

    :return: the stacked astropy.table
    """
    # set function name
    _ = display_func('vstack_cols', __NAME__)
    # deal with empty list
    if len(tablelist) == 0:
        # append a None
        return None
    elif len(tablelist) == 1:
        # append the single row
        return tablelist[0]
    else:
        # get column names
        columns = tablelist[0].colnames
        # get value dictionary
        valuedict = dict()
        for col in columns:
            valuedict[col] = []
        # loop around elements in tablelist
        for it, table_it in enumerate(tablelist):
            # loop around columns and add to valudict
            for col in columns:
                # must catch instances of astropy.table.row.Row as
                #   they are not a list
                if isinstance(table_it, Table.Row):
                    valuedict[col] += [table_it[col]]
                # else we assume they are astropy.table.Table
                else:
                    valuedict[col] += list(table_it[col])
        # push into new table
        newtable = Table()
        for col in columns:
            newtable[col] = valuedict[col]
        # vstack all rows
        return newtable


# =============================================================================
# Define working functions
# =============================================================================
def _get_non_telluric_stars(params, indexdb: IndexDatabase,
                            tstars: List[str]) -> List[str]:
    """
    Takes a table and gets all objects (OBJ_DARK and OBJ_FP) that are not in
    tstars (telluric stars)

    :param params:
    :param indexdb:
    :param tstars:
    :return:
    """
    # add to debug log
    WLOG(params, 'debug', textentry('90-503-00015'))
    # deal with no tstars
    if drs_text.null_text(tstars, ['None', '']):
        tstars = []
    # define the conditions for objects
    dprtypes = params.listp('REPROCESS_OBJ_DPRTYPES', dtype=str)
    # get the dprtype condition
    subcond = []
    for dprtype in dprtypes:
        subcond.append('KW_DPRTYPE="{0}"'.format(dprtype))
    condition = '({0})'.format(' OR '.join(subcond))
    # obstype must be OBJECT
    condition += ' AND KW_OBSTYPE="OBJECT"'
    # get columns from index database
    raw_objects = indexdb.get_entries(OBJNAMECOL, block_kind='raw',
                                      condition=condition)
    # deal with no table
    #    (can happen when coming from mk_tellu_db or fit_tellu_db etc)
    if len(raw_objects) == 0:
        return []
    # ----------------------------------------------------------------------
    # lets narrow down our list
    # ----------------------------------------------------------------------
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
    WLOG(params, 'debug', textentry('90-503-00016', args=[len(other_objects)]))
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
    pconst = constants.pload()
    if OBJNAMECOL in table:
        # original objnames
        objnames = table[OBJNAMECOL]
        # need to map values by new drs obj name
        table[OBJNAMECOL] = list(map(pconst.DRS_OBJ_NAME, objnames))
    # return table
    return table


def _get_recipe_module(params, **kwargs):
    func_name = __NAME__ + '.get_recipe_module()'
    # log progress: loading recipe module files
    WLOG(params, '', textentry('40-503-00014'))
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
            WLOG(params, 'error', textentry('00-503-00011', args=eargs))


def _get_filters(params, srecipe):
    # set up function name
    func_name = __NAME__ + '._get_filters()'
    # get pseudo constatns
    pconst = constants.pload()
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
                    tellu_include_list = telluric.get_tellu_include_list(params)
                    # note we need to update this list to match
                    # the cleaning that is done in preprocessing
                    clist = list(map(pconst.DRS_OBJ_NAME, tellu_include_list))
                    # add cleaned obj list to filters
                    filters[key] = list(clist)
                else:
                    continue
            # else assume we have a special list that is a string list
            #   (i.e. SCIENCE_TARGETS = "target1, target2, target3"
            elif isinstance(user_filter, str):
                objlist = _split_string_list(user_filter)
                # note we need to update this list to match
                # the cleaning that is done in preprocessing
                clist = list(map(pconst.DRS_OBJ_NAME, objlist))
                # add cleaned obj list to filters
                filters[key] = list(clist)
                if value == 'SCIENCE_TARGETS':
                    # update science targets
                    params.set('SCIENCE_TARGETS', value=', '.join(clist))
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
            WLOG(params, 'error', textentry('00-503-00017', args=eargs))
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
                WLOG(params, 'error', textentry('00-503-00013', args=eargs))
                cores = 1
            except Exception as e:
                eargs = [type(e), e]
                WLOG(params, 'error', textentry('00-503-00014', args=eargs))
                cores = 1
            # update the value in params
            params.set('CORES', value=cores, source='USER INPUT')

    # get number of cores
    if 'CORES' in params:
        try:
            cores = int(params['CORES'])
        except ValueError as e:
            eargs = [params['CORES'], type(e), e]
            WLOG(params, 'error', textentry('00-503-00006', args=eargs))
            cores = 1
        except Exception as e:
            eargs = [type(e), e]
            WLOG(params, 'error', textentry('00-503-00007', args=eargs))
            cores = 1
    else:
        cores = 1
    # get number of cores on machine
    cpus = os.cpu_count()
    # check that cores is valid
    if cores < 1:
        WLOG(params, 'error', textentry('00-503-00008', args=[cores]))
    if cores >= cpus:
        eargs = [cpus, cores]
        WLOG(params, 'warning', textentry('00-503-00009', args=eargs))
    # return number of cores
    return cores


def _group_progress(params, g_it, grouplist, groupname):
    # get message
    wargs = [' * ', g_it + 1, len(grouplist), groupname]
    # log
    WLOG(params, 'info', '', colour='magenta')
    WLOG(params, 'info', params['DRS_HEADER'], colour='magenta')
    WLOG(params, 'info', textentry('40-503-00018', args=wargs),
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


def _remove_engineering(params, indexdb, condition):
    global REMOVE_ENG_DIRS

    # if we are dealing with the trigger run do not do this -- user has
    #   specified a night
    if params['INPUTS']['TRIGGER']:
        return ''
    # get observation directory
    itable = indexdb.get_entries('OBS_DIR, KW_OBSTYPE', condition=condition)
    # get observation directory and observation types
    obs_dirs = np.array(itable['OBS_DIR'])
    obstypes = np.array(itable['KW_OBSTYPE'])
    # get unique nights
    u_obs_dirs = np.unique(obs_dirs)
    # get the object mask (i.e. we want to know that we have objects for this
    #   night
    objmask = obstypes == 'OBJECT'
    # define empty keep mask
    reject_obs_dirs = ''
    # loop around nights
    for obs_dir in u_obs_dirs:
        # get night mask
        nightmask = obs_dirs == obs_dir
        # joint mask
        nightobjmask = nightmask & objmask
        # if we find objects then keep all files from this night
        if np.sum(nightobjmask) == 0:
            # add to keep mask
            reject_obs_dirs += ' AND OBS_DIR != "{0}"'.format(obs_dir)
            # add to global variable
            if obs_dir not in REMOVE_ENG_DIRS:
                # log message
                wmsg = textentry('10-503-00014', args=[obs_dir])
                WLOG(params, 'warning', wmsg)
                # add to remove eng nights (so log message not produced again)
                REMOVE_ENG_DIRS.append(obs_dir)
    # return condition
    return reject_obs_dirs


def _group_drs_files(params: ParamDict, drstable: Table,
                     obs_dir_col: Union[str, None] = None,
                     seq_col: Union[str, None] = None,
                     time_col: Union[str, None] = None,
                     limit: Union[int, None] = None) -> Table:
    """
    Take a table (astropy.table.Table) "drstable" and sort them
    by observation time - such that if the sequence number increases
    (info stored in seq_col) files should be grouped together. If next entry
    has a sequence number lower than previous seqeunce number this is a new
    group of files.
    Note "drstable" must only contain rows with same (DrsFitsFile) type of files
    i.e. they are meant to be compared as part of the same group (if the follow
    sequentially)

    :param params: ParamDict, parameter dictionary of constants
    :param drstable: astropy.table.Table - the table of files where all
                     rows should be files of the same DrsFitsFile type
                     i.e. all FLAT_FLAT
    :param obs_dir_col: str or None, if set overrides
                      params['REPROCESS_OBSDIR_COL']
                      - which sets which column in drstable has the obs_dir
                      sub-directory information
    :param seq_col: str or None, if set overrides params['REPROCESS_SEQCOL']
                    - which sets the sequence number column i.e.
                    1,2,3,4,1,2,3,1,2,3,4  is 3 groups of objects (4,3,4)
                    when sorted in time (by 'time_col')
    :param time_col: str or None, if set overrides params['REPROCESS_TIMECOL']
                    - which is the column to sort the drstable by (and thus
                    put sequences in time order) - must be a float time
                    (i.e. MJD) in order to be sortable
    :param limit: int or None, if set sets the number of files allowed to be
                  in a group - if group gets to more than this many files starts
                  a new group (i.e. may break-up sequences) however new
                  sequences should start a new group even if less than limit
                  number
    :return: astropy.table.Table - the same drstable input - but with two
             new columns 'GROUPS' - the group number for each object, and
             'MEANDATE' - the mean of time_col for that group (helps when
             trying to match groups of differing files
    """

    # set function name
    func_name = display_func('_group_drs_files', __NAME__)
    # get properties from params
    night_col = pcheck(params, 'REPROCESS_OBSDIR_COL', func=func_name,
                       override=obs_dir_col)
    seq_colname = pcheck(params, 'REPROCESS_SEQCOL', func=func_name,
                         override=seq_col)
    time_colname = pcheck(params, 'REPROCESS_TIMECOL', func=func_name,
                          override=time_col)
    # deal with limit unset
    if limit is None:
        limit = np.inf
    # sort drstable by time column
    sortmask = np.argsort(drstable[time_colname])
    drstable = drstable[sortmask]
    # st up empty groups
    groups = np.zeros(len(drstable))
    # get the sequence column
    sequence_col = drstable[seq_colname]
    # start the group number at 1
    group_number = 0
    # set up night mask
    valid = np.zeros(len(drstable), dtype=bool)
    # by night name
    for night in np.unique(list(drstable[night_col])):
        # deal with just this night name
        nightmask = drstable[night_col] == night
        # deal with only one file in nightmask
        if np.sum(nightmask) == 1:
            group_number += 1
            groups[nightmask] = group_number
            valid |= nightmask
            continue
        # set invalid sequence numbers to 1
        sequence_mask = sequence_col.astype(str) == ''
        sequence_col[sequence_mask] = 1
        # get the sequence number
        sequences = sequence_col[nightmask].astype(int)
        indices = np.arange(len(sequences))
        # get the raw groups
        rawgroups = np.array(-(sequences - indices) + 1)
        # set up group mask
        nightgroup = np.zeros(np.sum(nightmask))
        # loop around the unique groups and assign group number
        for rgroup in np.unique(rawgroups):
            # new group
            group_number += 1
            # set up sub group parameters
            subgroupnumber, it = 0, 0
            # get group mask
            groupmask = rawgroups == rgroup
            # get positions
            positions = np.where(groupmask)[0]
            # deal with limit per group
            if np.sum(groupmask) > limit:
                # loop around all elements in group (using groupmask)
                while it < np.sum(groupmask):
                    # find how many are in this grup
                    subgroupnumber = np.sum(nightgroup == group_number)
                    # if we are above limit then start a new group
                    if subgroupnumber >= limit:
                        group_number += 1
                    nightgroup[positions[it]] = group_number
                    # iterate
                    it += 1
            else:
                # push the group number into night group
                nightgroup[groupmask] = group_number

        # add the night group to the full group
        groups[nightmask] = nightgroup
        # add to the valid mask
        valid |= nightmask

    # add groups and valid to dict
    drstable['GROUPS'] = groups
    # mask by the valid mask
    drstable = drstable[valid]

    # now work out mean time for each group
    # start of mean dates as zeros
    meandate = np.zeros(len(drstable))
    # get groups from table
    groups = drstable['GROUPS']
    # loop around each group and change the mean date for the files
    for g_it in range(1, int(max(groups)) + 1):
        # group mask
        groupmask = (groups == g_it)
        # group mean
        groupmean = np.mean(drstable[time_colname][groupmask])
        # save group mean
        meandate[groupmask] = groupmean
    # add meandate to drstable
    drstable['MEANDATE'] = meandate
    # return the group
    return drstable


def _get_argposorder(recipe: DrsRecipe, argdict: Dict[str, ArgDictType],
                     kwargdict: Dict[str, ArgDictType]
                     ) -> Tuple[List[str], Dict[str, ArgDictType]]:
    """
    Get the arguent position order

    Take the dictionaries of arguments and figure out which order these
    positional arguments and keyword arguments should be in for this recipe
    i.e. cal_extract  directory comes before files and before optional arguments

    for positional arguments this is defined by recipe.args[{arg}].pos,
    for optional arguments they are added to the end in whichever order they
    come

    :param recipe: DrsRecipe, the recipe instance these arguments belong to
    :param argdict: dictionary of values for each of the positional arguments
                   (each key is a positional argument name, each value is the
                    value that argument should have i.e.
                    directory should have value '2019-04-20'
                    --> dict(directory='2019-04-20', files=[file1, file2])
    :param kwargdict: dictionary of values for each of the optional arguments
                      (each key is an optional argument name, each value is the
                      value that argument should have i.e.
                      --{key}={value}    --plot=1
                      --> dict(plot=1)
    :return: tuple,
             1. runorder: list of strings of argument names, in the correct
                order - the value is the name of the argument
                (i.e. DrsArgument.name),
             2. rundict: a dictionary where the keys are the argument name and
                the value are a dictionary of DrsFitFile names and the values
                of these are astropy.table.Tables containing the
                files associated with this [argument][drsfile]
    """
    # set function name
    _ = display_func('_get_argposorder', __NAME__)
    # set up storage
    runorder = OrderedDict()
    # get args/kwargs from recipe
    args = recipe.args
    kwargs = recipe.kwargs
    # iterator for non-positional variables
    it = 0
    # loop around args
    for argname in args.keys():
        # must be in rundict keys
        if argname not in argdict.keys():
            continue
        # get arg
        arg = args[argname]
        # deal with non-required arguments when argdict has no values
        #    these are allowed only if arg.reprocess is True
        #    we skip adding to runorder
        if hasattr(argdict[argname], '__len__'):
            arglen = len(argdict[argname])
            if arg.reprocess and not arg.required and (arglen == 0):
                continue
        # get position or set it using iterator
        if arg.pos is not None:
            runorder[arg.pos] = argname
        else:
            runorder[1000 + it] = argname
            it += 1
    # loop around args
    for kwargname in kwargs.keys():
        # must be in rundict keys
        if kwargname not in kwargdict.keys():
            continue
        # get arg
        kwarg = kwargs[kwargname]
        # deal with non-required arguments when argdict has no values
        #    these are allowed only if arg.reprocess is True
        #    we skip adding to runorder
        if hasattr(kwargdict[kwargname], '__len__'):
            kwarglen = len(kwargdict[kwargname])
            if kwarg.reprocess and not kwarg.required and (kwarglen == 0):
                continue
        # get position or set it using iterator
        if kwarg.pos is not None:
            runorder[kwarg.pos] = kwargname
        else:
            runorder[1000 + it] = kwargname
            it += 1
    # recast run order into a numpy array of strings
    sortrunorder = np.argsort(list(runorder.keys()))
    runorder = np.array(list(runorder.values()))[sortrunorder]
    # merge argdict and kwargdict
    rundict = dict()
    for rorder in runorder:
        if rorder in argdict:
            rundict[rorder] = argdict[rorder]
        else:
            rundict[rorder] = kwargdict[rorder]
    # return run order and run dictionary
    return list(runorder), rundict


def _gen_run(params: ParamDict, rundict: Dict[str, ArgDictType],
             runorder: List[str], obs_dir: Union[str, None] = None,
             meantime: Union[float, None] = None,
             arg0: Union[str, None] = None, gtable0: Union[Table, None] = None,
             master_obs_dir: bool = False) -> List[Dict[str, Any]]:
    """
    Generate a recipe run dictionary of arguments based on the argument position
    order and if a secondary argument has a list of files match appriopriately
    with arg0 (using meantime) - returns a list of runs of this recipe
    where each entry is a dictionary where the key is the argument name and the
    value is the value(s) that argument can take

    :param params: ParamDict, parameter dictionary of constants
    :param rundict: a dictionary where the keys are the argument name and the
                    value are a dictionary of DrsFitFile names and the values
                    of these are astropy.table.Tables containing the
                    files associated with this [argument][drsfile]
    :param runorder: list of strings, the argument names in the correct order
    :param obs_dir: str or None, sets the night name (i.e. directory) for
                      this recipe run (if None set from params['OBS_DIR']
    :param meantime: float or None, sets the mean time (as MJD) for this
                     argument (associated to a set of files) - used when we have
                     a second set of files that need to be matched to the first
                     set of files, if not set meantime = 0.0
    :param arg0: str or None, if set this is the name of the first argument
                 that contains files (name comes from DrsArgument.name)
    :param gtable0: astropy.table.Table or None, if set this is the the case
                    where argname=arg0, and thus the file set should come from
                    a list of files
    :param master_obs_dir: bool, if True this is a master recipe, and therefore
                        the obs_dir should be the master observation directory,
                        master observation directory is obtained from
                        params['MASTER_OBS_DIR']

    :return: a list of runs of this recipe where each entry is a dictionary
             where the key is the argument name and the value is the value(s)
             that argument can take
    """
    # set function name
    _ = display_func('_gen_run', __NAME__)
    # deal with unset values (not used)
    if arg0 is None:
        arg0 = ''
    if gtable0 is None:
        gtable0 = dict(filecol=None)
    if obs_dir is None:
        obs_dir = params['OBS_DIR']
    if master_obs_dir:
        obs_dir = params['MASTER_OBS_DIR']
    if meantime is None:
        meantime = 0.0

    # need to find any argument that is not files but is a list
    pkeys, pvalues = [], []
    for argname in runorder:
        # only do this for numpy arrays and lists (not files)
        if isinstance(rundict[argname], (np.ndarray, list)):
            # append values to storage
            pvalues.append(list(rundict[argname]))
            pkeys.append(argname)
    # convert pkey to array
    pkeys = np.array(pkeys)
    # we assume we want every combination of arguments (otherwise it is
    #   more complicated)
    if len(pkeys) != 0:
        combinations = list(itertools.product(*pvalues))
    else:
        combinations = [None]
    # storage for new runs
    new_runs = []
    # loop around combinations
    for combination in combinations:
        # get dictionary storage
        new_run = dict()
        # loop around argnames
        for argname in runorder:
            # deal with having combinations
            if combination is not None and argname in pkeys:
                # find position in combinations
                pos = np.where(pkeys == argname)[0][0]
                # get value from combinations
                value = combination[pos]
            else:
                value = rundict[argname]
            # ------------------------------------------------------------------
            # if we are dealing with the first argument we have this
            #   groups files (gtable0)
            if argname == arg0:
                new_run[argname] = list(gtable0['OUT'])
            # if we are dealing with 'directory' set it from obs_dir
            elif argname == 'obs_dir':
                new_run[argname] = obs_dir
            # if we are not dealing with a list of files just set value
            elif not isinstance(value, OrderedDict):
                new_run[argname] = value
            # else we are dealing with another list and must find the
            #   best files (closest in time) to add that match this
            #   group
            else:
                margs = [params, argname, rundict, obs_dir, meantime]
                new_run[argname] = _match_group(*margs)
        # append new run to new runs
        new_runs.append(new_run)
    # return new_runs
    return new_runs


def _find_first_filearg(params: ParamDict, runorder: List[str],
                        argdict: Dict[str, Dict[str, Table]],
                        kwargdict: Dict[str, Dict[str, Table]]
                        ) -> Union[Tuple[str, Dict[str, Table]], None]:
    """
    Find the first file-type argument in a set of arguments
    If none exist return None, else return the argument name of the first
    file-type argument, and the values it can have (from argdict/kwargdict)

    :param params: ParamDict, parameter dictionary of constants
    :param runorder: list of strings, the argument names in the correct run
                     order
    :param argdict: dictionary of positional arguments (key = argument name,
                    value =  dictionary of Tables, where each sub-key is a
                    drsFitsFile type (str) and the values are astropy tables
    :param kwargdict: dictionary of optional arguments (key = argument name,
                    value =  dictionary of Tables, where each sub-key is a
                    drsFitsFile type (str) and the values are astropy tables
    :return: tuple, 1. the argument name of the first file argumnet,
             2. the dictionary of drs file tables for this argument
    """
    # set function name
    _ = display_func('_find_first_filearg', __NAME__)
    # loop around the run order
    for argname in runorder:
        # if argument is a positional argument return the argdict dictionary
        # of tables
        if argname in argdict:
            # it could be None here (if None supplied) so check argdict is
            #   a dictionary as expected
            if isinstance(argdict[argname], OrderedDict):
                return argname, argdict[argname]
        # else if the argument is an optional argument
        elif argname in kwargdict:
            # it could be None here (if None supplied) so check kwargdict is
            #   a dictionary as expected
            if isinstance(kwargdict[argname], OrderedDict):
                return argname, kwargdict[argname]
    # if we get to here we don't have a file argument (or it had no files)
    #   therefore return None --> deal with a None call on return
    return None


def _find_next_group(argname: str, drstable: Table,
                     usedgroups: Dict[str, List[str]],
                     groups: np.ndarray, ugroups: np.ndarray
                     ) -> Tuple[Union[Table, None], Dict[str, List[str]]]:
    """
    Find the next file group in a set of arguments

    :param argname: str, the name of the argument containing the first set of
                    files
    :param drstable: Table, the astropy.table.Table containing same DrsFitsFiles
                     entries (valid for this argument)
    :param usedgroups: dictionary of lists of strings - the previously used
                       group names, where each key is an argument name, and
                       each value is a list of group names that belong to
                       that argument
    :param groups: numpy array (1D), the full list of group names (as strings)
    :param ugroups: numpy array (1D), the unique + sorted list of group names
                    (as strings)
    :return: tuple, 1. the Table corresponding to the next group of files,
             2, dictionary of lists of strings - the previously used group
             names - where each key is an argument name, and each value is a
             list of group names that belong to that argument
    """
    # set function name
    _ = display_func('_find_next_group', __NAME__)
    # make sure argname is in usedgroups
    if argname not in usedgroups:
        usedgroups[argname] = []
    # get the arg group for this arg name
    arggroup = list(usedgroups[argname])
    # find all ugroups not in arggroup
    mask = np.in1d(ugroups, arggroup)
    # deal with all groups already found
    if np.sum(~mask) == 0:
        return None, usedgroups
    # get the next group
    group = ugroups[~mask][0]
    # find rows in this group
    mask = groups == group
    # add group to used groups
    usedgroups[argname].append(group)
    # return masked table and usedgroups
    return Table(drstable[mask]), usedgroups


def _match_group(params: ParamDict, argname: str,
                 rundict: Dict[str, ArgDictType],
                 obs_dir: Union[str, None], meantime: float,
                 nightcol: Union[str, None] = None) -> List[str]:
    """
    Find the best group  of files from 'argname' (table of files taken from
    rundict) to a specific obs_dir + mean time (night name matched on
    column night_col or params['REPROCESS_OBSDIR_COL'], mean time matched on
    MEANDATE column)

    :param params: ParamDict, parameter dictionary of constnats
    :param argname: str, the argument name we are matching (not the one for
                    meantime) the one to get table in rundict[argname][drsfile]
    :param rundict: a dictionary where the keys are the argument name and the
                    value are a dictionary of DrsFitFile names and the values
                    of these are astropy.table.Tables containing the
                    files associated with this [argument][drsfile]
    :param obs_dir: str or None, if set the night name to match to
                     (do not consider any files not from the night name) -
                     obs_dir controlled by table in rundict[argname][*] column
                     'nightcol' or params['REPROCESS_OBSDIR_COL']
    :param meantime: float, the time to match (with time in column 'MEANDATE'
                     from table in rundict[argname][*])
    :param nightcol: str or None, if set the column name in rundict[argname][*]
                     table, if not set uses params['REPROCESS_OBSDIR_COL']
    :return: list of strings, the filenames that match the argument with
             obs_dir and meantime
    """
    # set function name
    func_name = display_func('_match_groups', __NAME__)
    # get parmaeters from params/kwargs
    night_col = pcheck(params, 'REPROCESS_OBSDIR_COL', func=func_name,
                       override=nightcol)
    # get drsfiles
    drsfiles1 = list(rundict[argname].keys())
    # storage of valid groups [group number, drsfile, meandate]
    valid_groups = []
    # loop around drs files in argname
    for drsfile in drsfiles1:
        # get table
        ftable1 = rundict[argname][drsfile]
        # mask by night name
        if obs_dir is not None:
            mask = ftable1[night_col] == obs_dir
        else:
            mask = np.ones(len(ftable1)).astype(bool)
        # check that we have some files with this obs_dir
        if np.sum(mask) == 0:
            continue
        # mask table
        table = Table(ftable1[mask])
        # get unique groups
        ugroups = np.unique(table['GROUPS']).astype(int)
        # loop around groups
        for group in ugroups:
            # mask group
            groupmask = table['GROUPS'] == group
            # get mean date
            groumeandate = table['MEANDATE'][groupmask][0]
            # store in valid_groups
            valid_groups.append([group, drsfile, groumeandate])
    # if we have no valid groups we cannot continue (time to stop)
    if len(valid_groups) == 0:
        raise DrsRecipeException('No valid groups')
    # for all valid_groups find the one closest intime to meantime of first
    #   argument
    valid_groups = np.array(valid_groups)
    # get mean times
    meantimes1 = np.array(valid_groups[:, 2]).astype(float)
    # ----------------------------------------------------------------------
    # find position of closest in time
    min_pos = int(np.argmin(abs(meantimes1 - meantime)))
    # ----------------------------------------------------------------------
    # get group for minpos
    group_s = int(valid_groups[min_pos][0])
    # get drsfile for minpos
    drsfile_s = valid_groups[min_pos][1]
    # get table for minpos
    table_s = rundict[argname][drsfile_s]
    # deal with table still being None
    if table_s is None:
        raise DrsRecipeException('No valid groups')
    # mask by group
    mask_s = np.array(table_s['GROUPS']).astype(int) == group_s
    # ----------------------------------------------------------------------
    # make sure mask has entries
    if np.sum(mask_s) == 0:
        raise DrsRecipeException('No valid groups')
    # ----------------------------------------------------------------------
    # return files for min position
    return list(table_s['OUT'][mask_s])


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

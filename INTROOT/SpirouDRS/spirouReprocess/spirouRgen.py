#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-10 at 13:38

@author: cook
"""
from __future__ import division
import numpy as np
import os
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

from SpirouDRS.spirouReprocess.redo import recipe_definitions as rd

import cal_BADPIX_spirou
import cal_CCF_E2DS_spirou
import cal_dark_master_spirou
import cal_DRIFT_E2DS_spirou
import cal_DRIFTPEAK_E2DS_spirou
import cal_DRIFTCCF_E2DS_spirou
import cal_exposure_meter
import cal_wave_mapper
import cal_extract_RAW_spirou
import cal_FF_RAW_spirou
import cal_HC_E2DS_EA_spirou
import cal_loc_RAW_spirou
import cal_SLIT_spirou
import cal_shape_master_spirou
import cal_shape_spirou
import cal_thermal_spirou
import cal_WAVE_E2DS_EA_spirou
import cal_preprocess_spirou
import off_listing_RAW_spirou
import off_listing_REDUC_spirou
import obj_mk_tellu_new
import obj_mk_tellu_db
import obj_fit_tellu
import obj_fit_tellu_db
import obj_mk_obj_template
import visu_RAW_spirou
import visu_E2DS_spirou
import pol_spirou


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouRgen.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get param dictionary
ParamDict = spirouConfig.ParamDict
# -----------------------------------------------------------------------------
# define which recipes have no night name argument
NO_NIGHTNAME = [obj_mk_tellu_db, cal_dark_master_spirou,
                obj_fit_tellu_db]
# define which group the recipes belong to
RAW_PROGRAMS = [cal_preprocess_spirou, off_listing_RAW_spirou]
TMP_PROGRAMS = [cal_BADPIX_spirou, cal_dark_master_spirou,
                cal_extract_RAW_spirou, cal_FF_RAW_spirou,
                cal_loc_RAW_spirou, cal_thermal_spirou,
                cal_SLIT_spirou, cal_shape_spirou,
                cal_shape_master_spirou, cal_exposure_meter, cal_wave_mapper,
                visu_RAW_spirou]
RED_PROGRAMS = [cal_CCF_E2DS_spirou, cal_DRIFT_E2DS_spirou,
                cal_DRIFTPEAK_E2DS_spirou, cal_DRIFTCCF_E2DS_spirou,
                cal_HC_E2DS_EA_spirou, cal_WAVE_E2DS_EA_spirou,
                off_listing_REDUC_spirou, obj_mk_tellu_new,
                obj_mk_tellu_db, obj_fit_tellu, obj_fit_tellu_db,
                obj_mk_obj_template, visu_E2DS_spirou, pol_spirou]

# define which recipes accept wildcards
ALLOW_WILDCARDS = ['cal_preprocess_spirou']

# -----------------------------------------------------------------------------
# define run lists
# -----------------------------------------------------------------------------
MOD_LIST = OrderedDict()
MOD_LIST['PREPROCESS'] = cal_preprocess_spirou
MOD_LIST['DARK_MASTER'] = cal_dark_master_spirou
MOD_LIST['BADPIX_MASTER'] = cal_BADPIX_spirou
MOD_LIST['LOC_MASTER'] = cal_loc_RAW_spirou
MOD_LIST['SHAPE_MASTER'] = cal_shape_master_spirou
MOD_LIST['MK_TELLU_DB'] = obj_mk_tellu_db
MOD_LIST['FIT_TELLU_DB'] = obj_fit_tellu_db
MOD_LIST['BADPIX'] = cal_BADPIX_spirou
MOD_LIST['LOC'] = cal_loc_RAW_spirou
MOD_LIST['SHAPE'] = cal_shape_spirou
MOD_LIST['FF'] = cal_FF_RAW_spirou
MOD_LIST['THERMAL'] = cal_thermal_spirou
MOD_LIST['WAVE'] = cal_WAVE_E2DS_EA_spirou
MOD_LIST['EXTRACT_TELLU'] = cal_extract_RAW_spirou
MOD_LIST['EXTRACT_OBJ'] = cal_extract_RAW_spirou
MOD_LIST['EXTRACT_ALL'] = cal_extract_RAW_spirou
MOD_LIST['KK_TELLU'] = obj_mk_tellu_new
MOD_LIST['FIT_TELLU'] = obj_fit_tellu

# -----------------------------------------------------------------------------
# define the key to identify runs in config file
RUN_KEY = 'ID'
# column names for run tables
ITABLE_FILECOL = 'FILENAME'
NIGHT_COL = '@@@NIGHTNAME'
ABSFILE_COL = '@@@ABSFILE'


# =============================================================================
# Define classes
# =============================================================================
class Run:
    def __init__(self, params, runstring, priority=0):
        self.params = params
        self.runstring = runstring
        self.priority = priority
        # get program names
        self._get_program_names()
        # get args
        self.args = runstring.split(' ')
        self.recipename = None
        self.recipemod = None
        self.nightname = None
        self.argstart = None
        self.kind = None
        self.kwargs = dict()
        # get properties
        self.get_recipe()
        self.get_nightname()
        self.get_kwargs()

    def _get_program_names(self):
        self.no_names = [remove_py(name.__NAME__) for name in NO_NIGHTNAME]
        self.raw_names = [remove_py(name.__NAME__) for name in RAW_PROGRAMS]
        self.tmp_names = [remove_py(name.__NAME__) for name in TMP_PROGRAMS]
        self.red_names = [remove_py(name.__NAME__) for name in RED_PROGRAMS]
        self.no_programs = NO_NIGHTNAME
        self.raw_programs = RAW_PROGRAMS
        self.tmp_programs = TMP_PROGRAMS
        self.red_programs = RED_PROGRAMS

    def get_recipe(self):
        # the first argument must be the recipe name
        self.recipename = self.args[0]
        # make sure recipe does not have .py on the end
        self.recipename = remove_py(self.recipename)
        # get recipe type (raw/tmp/reduced)
        if self.recipename in self.raw_names:
            self.kind = 0
            pos = self.raw_names.index(self.recipename)
            self.recipemod = self.raw_programs[pos]
        elif self.recipename in self.tmp_names:
            self.kind = 1
            pos = self.tmp_names.index(self.recipename)
            self.recipemod = self.tmp_programs[pos]
        elif self.recipename in self.red_names:
            self.kind = 2
            pos = self.red_names.index(self.recipename)
            self.recipemod = self.red_programs[pos]
        else:
            emsg1 = ('RunList Error: Recipe = "{0}" invalid'
                     ''.format(self.recipename))
            emsg2 = '\t Line: {0} {1}'.format(self.priority, self.runstring)
            WLOG(self.params, 'error', [emsg1, emsg2])
            self.kind = -1

    def get_nightname(self):
        # ------------------------------------------------------------------
        # get night name
        if self.recipename in self.no_names:
            self.nightname = ''
            self.argstart = 1
        else:
            try:
                self.nightname = self.args[1]
            except Exception as e:
                WLOG(self.params, 'error', 'Error {0}: {1}'.format(type(e), e))
            self.argstart = 2
            self.kwargs['night_name'] = self.nightname

    def get_kwargs(self):

        left_args = self.args[self.argstart:]
        req_args = self.recipemod.__args__[self.argstart -1:]

        # situation 1: number of required args = 1
        # solution 1: all left args are this req_args
        if len(req_args) == 1:
            self.kwargs[req_args[0]] = left_args

        # situation 2: number of required args = number of left args
        # solution 2: pipe each left arg into required args
        elif len(req_args) == len(left_args):
            for it in range(len(req_args)):
                self.kwargs[req_args[it]] = left_args[it]

        # situation 3: number of left args > number of required args
        # solution 3: pipe 1 left arg into each required args and then all
        #             remained in last required arg
        elif len(left_args) > len(req_args):
            jt = 0
            for it in range(len(left_args)):
                # here we are within required args limit --> 1 in each
                if it < len(req_args) - 1:
                    self.kwargs[req_args[it]] = left_args[it]
                    jt += 1
                # if we are at the point of adding make sure last arg is a list
                # --> start adding to last required arg
                elif it == len(req_args) - 1:
                    self.kwargs[req_args[jt]] = [self.kwargs[req_args[jt]]]
                    self.kwargs[req_args[jt]] += [left_args[it]]
                # else we are past the point and should just append to last
                # required arg
                else:
                    self.kwargs[req_args[jt]] += [left_args[it]]

        # situation 4: number of left args < number of required args
        # solution 4: fill up as many as possible
        elif len(left_args) < len(req_args):
            # loop around left_args
            for it in range(len(left_args)):
                # we just add one left_arg to each available req_args
                self.kwargs[req_args[it]] = left_args[it]

        # ------------------------------------------------------------------
        # remove any keyword arguments that are empty
        kwargs = dict()
        for kwarg in self.kwargs:
            if len(self.kwargs[kwarg]) != 0:
                kwargs[kwarg] = self.kwargs[kwarg]
        self.kwargs = kwargs

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Run[{0}]'.format(self.runstring)


# =============================================================================
# Define user functions
# =============================================================================
def generate(params, tables, paths, runtable):

    # get all values (upper case) using map function
    rvalues = list(map(lambda x: x.upper(), runtable.values()))
    # sort out which mode we are in
    if 'ALL' in rvalues:
        return generate_all(params, tables, paths)
    else:
        return generate_ids(params, tables, paths, runtable)


# =============================================================================
# Define "from id" functions
# =============================================================================
def generate_ids(params, tables, paths, runtable):

    # should just need to sort these
    numbers = np.array(list(runtable.keys()))
    commands = np.array(list(runtable.values()))
    # sort by number
    sortmask = np.argsort(numbers)
    # get sorted run list
    runlist = list(commands[sortmask])
    keylist = list(numbers[sortmask])
    # iterate through and make run objects
    run_objects = []

    for it, run_item in enumerate(runlist):
        # create run object
        run_object = Run(params, run_item, priority=keylist[it])
        # append to list
        run_objects.append(run_object)
    # check list files against tables and assign a group
    run_objects = check_runlist(params, run_objects)

    # return run objects
    return run_objects


def check_runlist(params, runlist):
    # ------------------------------------------------------------------
    # storage of outlist
    out_runlist = []
    # ------------------------------------------------------------------
    for it, run_item in enumerate(runlist):
        # check that we want to run this recipe
        check = False
        # ------------------------------------------------------------------
        # find run_item in MOD_LIST
        for key in MOD_LIST:
            # get run_key
            runkey = 'RUN_{0}'.format(key)
            rl_item = MOD_LIST[key]
            # check if recipe names agree
            cond1 = run_item.recipename == remove_py(rl_item.__NAME__)
            # check if key in params
            cond2 = runkey in params
            # if both conditions met then we take the condition from params
            if cond1 and cond2:
                check = params[runkey]
                break
            # if we don't have key in params and key isn't in MOD_LIST we should
            #   just pass
            elif not (cond1 and cond2):
                check = True
                break
        # ------------------------------------------------------------------
        # append to output
        if check:
            out_runlist.append(run_item)
    # return out list
    return out_runlist


# =============================================================================
# Define "from automated" functions
# =============================================================================
def generate_all(params, tables, paths):
    return []
    # storage of runlist
    runtable = dict()
    runkey = 0
    # loop around each module and find arguments
    for modname in MOD_LIST:
        # get recipe name
        recipename = MOD_LIST[modname].__NAME__
        recipeargs = MOD_LIST[modname].__args__
        # get run name
        runname = 'RUN_{0}'.format(modname)
        # make sure item in params - skip if it isn't
        if runname not in params:
            continue
        # make sure run list item is True in params
        if params[runname]:
            # find the recipe defintion
            recipe = find_recipe(recipename)
            # for now if recipe is None just skip
            if recipe is None:
                continue
            # get associated file types
            req_args = find_required_arguments(recipe, recipeargs)
            # using the required arguments to generate a set of runlist entries
            gargs = [recipe, req_args, tables, paths, MOD_LIST[modname]]
            commands = generate_run_commands(params, *gargs)
            # add this to runlist
            for key in commands.keys():
                runtable[runkey + key] = commands[key]
    # return run objects (via generate ids)
    return generate_ids(params, tables, paths, runtable)


def find_recipe(recipename):
    for recipe in rd.recipes:
        if recipename == recipe.name:
            return recipe
    else:
        return None


def find_required_arguments(recipe, recipeargs):
    # storage for output arguments
    outargs = dict()
    # get recipe arg list without '-'
    recipearglist = list(map(lambda x: x.replace('-', ''), recipe.args.keys()))
    for rarg in recipeargs:
        if rarg in recipearglist:
            outargs[rarg] = recipe.args[rarg]['files']
    return outargs


def generate_run_commands(params, recipe, args, tables, paths, module):

    # get the raw table
    rawtable = tables[0]

    # storage of output commands
    commands = OrderedDict()

    # define the keys
    number = 0

    outargs = OrderedDict()
    # loop around arguments
    for argname in args:
        # get drs files
        drsfiles = args[argname]
        # set up a mask of the table
        mask = np.zeros_like(rawtable[ITABLE_FILECOL], dtype=bool)
        # set up storage for new filenames
        newfilenames = np.array(rawtable[ITABLE_FILECOL])
        # loop around files
        for drsfile in drsfiles:
            # get new files onto outargs
            mask_it, newfiles = get_drs_file_mask(drsfile, rawtable)
            newfilenames[mask_it] = newfiles
            mask |= mask_it
        # add the new file names to the rawtable
        rawtable['NEWFILENAME'] = newfilenames
        # get the group number
        groups = group_drs_files(mask, rawtable)
        rawtable['GROUPS'] = groups

        outargs[argname] = rawtable[mask].copy()


    return commands



def get_drs_file_mask(drsfile, table):
    # get in filenames
    infilenames = table[ITABLE_FILECOL]
    # -------------------------------------------------------------------------
    # get output extension
    outext = drsfile.args['ext']
    # get input extension
    while 'intype' in drsfile.args:
        drsfile = drsfile.args['intype']
    inext = drsfile.args['ext']
    # -------------------------------------------------------------------------
    # get required header keys
    rkeys = dict()
    for arg in drsfile.args:
        if arg.startswith('KW_'):
            rkeys[arg] = drsfile.args[arg]
    # maask by the required header keys
    mask = np.ones_like(infilenames, dtype=bool)
    for key in rkeys:
        mask &= table[key] == rkeys[key]
    # -------------------------------------------------------------------------
    # construct new filenames
    outfilenames = []
    for it, filename in enumerate(infilenames):
        if not filename.endswith(inext):
            mask[it] = False
        if mask[it]:
            outfilenames.append(filename.replace(inext, outext))
    # -------------------------------------------------------------------------
    # return the mask
    return mask, outfilenames


def group_drs_files(inmask, table):

    groups = np.zeros(len(table))

    # get the sequence column
    sequence_col = table['KW_CMPLTEXP']
    # start the group number at 1
    group_number = 1
    # by night name
    for night in np.unique(table[NIGHT_COL]):
        # deal with just this night name
        nightmask = table[NIGHT_COL] == night
        # remove any with invalid sequence numbers
        nightmask &= (sequence_col != '') & inmask
        # get the sequence number
        sequences = sequence_col[nightmask].astype(int)
        indices = np.arange(len(sequences))
        # get the raw groups
        rawgroups = np.array(-(sequences - indices) + 1)

        nightgroup = np.zeros(np.sum(nightmask))
        # loop around the unique groups and assign group number
        for rgroup in np.unique(rawgroups):
            # get group mask
            groupmask = rawgroups == rgroup
            # push the group number into night group
            nightgroup[groupmask] = group_number
            # add to the group number
            group_number += 1
        # add the night group to the full group
        groups[nightmask] = nightgroup
    # return the group
    return groups




# =============================================================================
# Define  worker functions
# =============================================================================
def remove_py(innames):
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


def check_run_params(params, run_item):

    # if we get to here then check has failed
    return False


# =============================================================================
# End of code
# =============================================================================

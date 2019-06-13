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
from SpirouDRS import spirouTelluric
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
MOD_LIST['PREPROCESS'] = [cal_preprocess_spirou, None]
MOD_LIST['DARK_MASTER'] = [cal_dark_master_spirou, None]
MOD_LIST['BADPIX_MASTER'] = [cal_BADPIX_spirou, None]
MOD_LIST['LOC_MASTER'] = [cal_loc_RAW_spirou, None]
MOD_LIST['SHAPE_MASTER'] = [cal_shape_master_spirou, None]
MOD_LIST['BADPIX'] = [cal_BADPIX_spirou, None]
MOD_LIST['LOC'] = [cal_loc_RAW_spirou, None]
MOD_LIST['SHAPE'] = [cal_shape_spirou, None]
MOD_LIST['FF'] = [cal_FF_RAW_spirou, None]
MOD_LIST['THERMAL'] = [cal_thermal_spirou, None]
MOD_LIST['EXTRACT_FPHC'] = [cal_extract_RAW_spirou, ['FP_FP', 'HC_HC']]
MOD_LIST['WAVE'] = [cal_WAVE_E2DS_EA_spirou, None]
MOD_LIST['EXTRACT_TELLU'] = [cal_extract_RAW_spirou, ['TELLURIC_TARGETS']]
MOD_LIST['EXTRACT_OBJ'] = [cal_extract_RAW_spirou, ['SCIENCE_TARGETS']]
MOD_LIST['EXTRACT_ALL'] = [cal_extract_RAW_spirou, None]
MOD_LIST['MK_TELLU_DB'] = [obj_mk_tellu_db, None]
MOD_LIST['FIT_TELLU_DB'] = [obj_fit_tellu_db, None]
MOD_LIST['MK_TELLU'] = [obj_mk_tellu_new, ['TELLURIC_TARGETS']]
MOD_LIST['FIT_TELLU'] = [obj_fit_tellu, ['SCIENCE_TARGETS']]

# -----------------------------------------------------------------------------
# define the key to identify runs in config file
RUN_KEY = 'ID'
# column names for run tables
ITABLE_FILECOL = 'FILENAME'
NIGHT_COL = '@@@NIGHTNAME'
ABSFILE_COL = '@@@ABSFILE'

# filters
SFILTER = 'SCIENCE_TARGETS'
TFILTER = 'TELLURIC_TARGETS'
FP_FILTER = 'FP_FP'
HC_FILTER = 'HC_HC'

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
            rl_item = MOD_LIST[key][0]
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
    # storage of runlist
    runtable = OrderedDict()
    runkey = 0
    # loop around each module and find arguments
    for m_it, modname in enumerate(MOD_LIST):
        # log progress
        WLOG(params, '', 'Checking run {0}'.format(modname))
        # get recipe name
        recipename = MOD_LIST[modname][0].__NAME__
        recipeargs = np.array(MOD_LIST[modname][0].__args__)
        recipereqs = np.array(MOD_LIST[modname][0].__required__)
        recipefilter = MOD_LIST[modname][1]
        if len(recipeargs) > 0 and len(recipereqs) > 0:
            recipeargs = list(recipeargs[recipereqs])
        # get run name
        runname = 'RUN_{0}'.format(modname)
        # make sure item in params - skip if it isn't
        if runname not in params:
            continue
        # make sure run list item is True in params
        if params[runname]:
            # log progress
            wmsg = '\tGenerating runs for {0} [{1}]'
            wargs = [modname, remove_py(recipename)]
            WLOG(params, '', wmsg.format(*wargs))
            # find the recipe defintion
            recipe = find_recipe(params, recipename)
            # for now if recipe is None just skip
            if recipe is None:
                continue
            # --------------------------------------------------------------
            # get associated file types
            req_args = find_required_arguments(recipe, recipeargs)
            # --------------------------------------------------------------
            # deal with no arguments
            if len(req_args) == 0:
                commands = OrderedDict()
                commands[0] = '{0}'.format(remove_py(recipename))
            else:
                # using the required arguments to generate a set of runlist
                # entries
                cargs = [recipe, req_args, tables, recipefilter]
                commands = generate_run_commands(params, *cargs)
            # --------------------------------------------------------------
            # add this to runlist
            for key in commands.keys():
                cargs = [runkey, commands[key]]
                print('Adding {0}: {1}'.format(*cargs))
                runtable[runkey] = commands[key]
                # iterate runkey
                runkey += 1
        # else print that we are skipping
        else:
            # log progress
            wmsg = '\t\tSkipping runs for {0} [{1}]'
            wargs = [modname, remove_py(recipename)]
            WLOG(params, '', wmsg.format(*wargs))

    # return run objects (via generate ids)
    return generate_ids(params, tables, paths, runtable)


# =============================================================================
# Define  worker functions
# =============================================================================
def find_recipe(params, recipename):
    for recipe in rd.recipes:
        if recipename == recipe.name:
            return recipe
    else:
        wmsg = '\tCannot find recipe "{0}" skipping.'
        WLOG(params, 'warning', wmsg.format(recipename))
        return None


def find_required_arguments(recipe, recipeargs):
    # storage for output arguments
    outargs = dict()
    # get recipe arg list without '-'
    recipearglist = list(map(lambda x: x.replace('-', ''), recipe.args.keys()))
    oarglist = list(recipe.args.keys())
    for rarg in recipeargs:
        if rarg in recipearglist:
            pos = recipearglist.index(rarg)
            oarg = oarglist[pos]
            outargs[oarg] = recipe.args[oarg]['files']
    return outargs


def generate_run_commands(params, recipe, args, tables, filters):
    # get the raw table
    rawtable = tables[0]
    # storage of output commands
    commands = OrderedDict()
    # command number
    number = 0
    # define the keys
    outargs = OrderedDict()
    # ----------------------------------------------------------------------
    # group the files
    # ----------------------------------------------------------------------
    # work out the mean date for each group
    meandate = np.zeros(len(rawtable))
    # loop around arguments
    for argname in args:
        # get the dtype
        dtype = recipe.args[argname]['dtype']
        # ------------------------------------------------------------------
        if dtype not in ['file', 'files']:
            continue
        # get drs files
        drsfiles = args[argname]
        # ------------------------------------------------------------------
        # set up a mask of the table
        mask = np.zeros_like(rawtable[ITABLE_FILECOL], dtype=bool)
        # set up storage for new filenames
        newfilenames = list(rawtable[ITABLE_FILECOL])
        # loop around files
        for drsfile in drsfiles:
            # get new files onto outargs
            dargs = [drsfile, rawtable, filters]
            mask_it, newfiles = get_drs_file_mask(params, *dargs)
            jt = 0
            for it in range(len(newfilenames)):
                if mask_it[it]:
                    newfilenames[it] = newfiles[jt]
                    jt += 1
            mask |= mask_it
        # add the new file names to the rawtable
        rawtable['NEWFILENAME'] = newfilenames
        # get the group number
        groups = group_drs_files(mask, rawtable)
        rawtable['GROUPS'] = groups
        # ------------------------------------------------------------------
        # loop around each group and change the mean date for the files
        for g_it in range(1, int(max(groups))):
            # group mask
            groupmask = (groups == g_it) & mask
            # group mean
            groupmean = np.mean(rawtable['KW_ACQTIME'][groupmask])
            # save group mean
            meandate[groupmask] = groupmean
        # add meant to table
        rawtable['MEANDATE'] = meandate
        # ------------------------------------------------------------------
        # separate the groups into smaller tables
        outargs[argname] = []
        # loop around groups and add to outargs
        for g_it in range(1, int(max(groups))):
            outargs[argname].append(rawtable[groups == g_it].copy())
    # ----------------------------------------------------------------------
    # sort out what to do with the groups
    # ----------------------------------------------------------------------
    # if we only have one file argument then we can put all files from a group
    #  into a run
    if len(outargs) == 1:
        # get the arg name
        argname = list(outargs.keys())[0]
        recipename = remove_py(recipe.name)
        recipeargs = recipe.args

        # need to deal with having a limit of 1 file
        if 'limit' in recipeargs[argname]:
            for group in outargs[argname]:
                # get the night name (should be the same for all)
                nightname = group[NIGHT_COL][0]
                # get the file list
                filelist = np.array(group['NEWFILENAME'])
                # loop around each file
                for filename in filelist:
                    # construct the command
                    cargs = [recipename, nightname, filename]
                    command_group = '{0} {1} {2}'.format(*cargs)
                    # append to command dict
                    commands[number] = command_group
                    # iterate the command number
                    number += 1
        else:
            # loop around groups
            for group in outargs[argname]:
                # get the night name (should be the same for all)
                nightname = group[NIGHT_COL][0]
                # get the file list
                filelist = np.array(group['NEWFILENAME'])
                # construct the command
                cargs = [recipename, nightname, ' '.join(filelist)]
                command_group = '{0} {1} {2}'.format(*cargs)
                # append to command dict
                commands[number] = command_group
                # iterate the command number
                number += 1
    # if we have more than one file argument just take the first file of
    #    each group
    #    we also have to match groups so that we have the correct files for
    #    both arguments
    else:
        # get the recipe name (command name)
        recipename = remove_py(recipe.name)
        # find the argument with the minimum number of groups
        # (this is the group we will match to)
        min_len, min_arg = np.inf, None
        for argname in outargs:
            if len(outargs[argname]) < min_len:
                min_len, min_arg = len(outargs[argname]), argname
        # get other args and setup storage for used groups in other args
        used_groups = dict()
        for argname in outargs:
            if argname != min_arg:
                used_groups[argname] = []
        # loop around groups in "min_arg" and match to other args
        #   Note they must be from the same night
        for group1 in outargs[min_arg]:
            # get the mean date for this group (all should be the same)
            meandate1 = group1['MEANDATE'][0]
            # get the night name (should be the same for all)
            night1 = group1[NIGHT_COL][0]
            # storage for the filelist
            # TODO: TAKE THE FIRST FILE FROM GROUP1
            filelist = [group1['NEWFILENAME'][0]]
            # find the group in other groups that is closest in time to
            # other "min arg group"
            margs = [outargs, used_groups, meandate1, night1, filelist]
            used_groups, filelist, found = match_groups(*margs)
            # finally if a group to match all groups was found ("found")
            # then we can construct a command run for this entry
            # of group1
            if found:
                # construct the command
                cargs = [recipename, night1, ' '.join(filelist)]
                command_group = '{0} {1} {2}'.format(*cargs)
                # append to command dict
                commands[number] = command_group
                # iterate the command number
                number += 1
    # return the command dictionary
    return commands


def get_drs_file_mask(params, drsfile, table, filters):


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
    # deal with filters
    if filters is not None:
        # ------------------------------------------------------------------
        # KW_OBJECT filters
        # ------------------------------------------------------------------
        # deal with science filter
        if params[SFILTER] is not None and SFILTER in filters:
            objectnames = params[SFILTER].split(' ')
            # apply object names to mask
            mask &= np.in1d(table['KW_OBJECT'], objectnames)
        # deal with telluric filter
        if TFILTER in filters:
            if params[TFILTER] is None:
                objectnames = spirouTelluric.GetWhiteList()
            else:
                objectnames = params[TFILTER].split(' ')
            # apply object names to mask
            mask &= np.in1d(table['KW_OBJECT'], objectnames)
        # ------------------------------------------------------------------
        # type filters
        # ------------------------------------------------------------------
        # type mask is initially all False
        typemask = np.zeros(len(table), dtype=bool)
        do_mask = False
        # deal with an FP filter
        if FP_FILTER in filters:
            # conditions to be FP_FP
            cond1 = table['KW_CCAS'] == 'pos_fp'
            cond2 = table['KW_CREF'] == 'pos_fp'
            # apply to mask
            typemask |= (cond1 & cond2)
            do_mask = True

        # deal with an HC filter
        if HC_FILTER in filters:
            # conditions to be FP_FP
            cond1 = table['KW_CCAS'] == 'pos_hc1'
            cond2 = table['KW_CREF'] == 'pos_hc1'
            # apply to mask
            typemask |= (cond1 & cond2)
            do_mask = True

        # apply type mask to mask (only if we need to)
        if do_mask:
            mask &= typemask

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


def match_groups(outargs, used_groups, meandate1, night1, filelist):
    found = True
    # find the group in other groups that is closest in time to
    # other "min arg group"
    for argname2 in used_groups.keys():
        # get the group2 filelist
        tables2 = outargs[argname2]
        # set up storage for mean dates of group2
        meandates2 = []
        # loop around groups in other group
        for g_it2, group2 in enumerate(tables2):
            # skip if in used_groups already
            if g_it2 in used_groups[argname2]:
                continue
            # get the night for group2
            night2 = group2[NIGHT_COL]
            # if not in the same night then skip
            if night1 != night2:
                continue
            # get the mean date for the other group
            meandates2.append(group2['MEANDATE'][0])
        # if meandates2 is empty then we need to skip this group1
        if len(meandates2) == 0:
            found = False
            break
        # find the closest group2 mean date to group1
        diff = np.abs(np.array(meandates2) - meandate1)
        closest = int(np.argmin(diff))
        # get the closest table in group2
        table2 = tables2[closest]
        # get the file list from closest group
        # TODO: TAKE THE FIRST FILE FROM GROUP2
        filelist.append(table2['NEWFILENAME'][0])
        # add to used_groups
        used_groups[argname2].append(closest)
    # return the used_groups and the updated filelist
    return used_groups, filelist, found


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

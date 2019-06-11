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

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

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
RUN_LIST = dict()
RUN_LIST['RUN_DARK_MASTER'] = cal_dark_master_spirou
RUN_LIST['RUN_BADPIX_MASTER'] = cal_BADPIX_spirou
RUN_LIST['RUN_LOC_MASTER'] = cal_loc_RAW_spirou
RUN_LIST['RUN_SHAPE_MASTER'] = cal_shape_master_spirou
RUN_LIST['RUN_MK_TELLU_DB'] = obj_mk_tellu_db
RUN_LIST['RUN_FIT_TELLU_DB'] = obj_fit_tellu_db
RUN_LIST['RUN_PREPROCESS'] = cal_preprocess_spirou
RUN_LIST['RUN_BADPIX'] = cal_BADPIX_spirou
RUN_LIST['RUN_LOC'] = cal_loc_RAW_spirou
RUN_LIST['RUN_SHAPE'] = cal_shape_spirou
RUN_LIST['RUN_FF'] = cal_FF_RAW_spirou
RUN_LIST['RUN_THERMAL'] = cal_thermal_spirou
RUN_LIST['RUN_WAVE'] = cal_WAVE_E2DS_EA_spirou
RUN_LIST['RUN_EXTRACT_TELLU'] = cal_extract_RAW_spirou
RUN_LIST['RUN_EXTRACT_OBJ'] = cal_extract_RAW_spirou
RUN_LIST['RUN_EXTRACT_ALL'] = cal_extract_RAW_spirou
RUN_LIST['RUN_MK_TELLU'] = obj_mk_tellu_new
RUN_LIST['RUN_FIT_TELLU'] = obj_fit_tellu

# -----------------------------------------------------------------------------
# define skip list
# -----------------------------------------------------------------------------
# Format = [module, input_suffices, output_suffices
SKIP_LIST = dict()
# preprocessing
inexts = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']
outexts = ['a_pp.fits', 'c_pp.fits', 'd_pp.fits', 'f_pp.fits', 'o_pp.fits']
SKIP_LIST['SKIP_PREPROCESS'] = [cal_preprocess_spirou, inexts, outexts]

# badpix
inexts, outexts = ['f_pp.fits'], ['f_pp_badpixel.fits']
SKIP_LIST['SKIP_BADPIX'] = [cal_BADPIX_spirou, inexts, outexts]

# loc
inexts = ['f_pp.fits', 'f_pp.fits']
outexts = ['f_pp_loco_AB.fits', 'f_pp_loco_C.fits']
SKIP_LIST['SKIP_LOC'] = [cal_loc_RAW_spirou, inexts, outexts]

# shape
inexts, outexts = ['a_pp.fits'], ['a_pp_shape.fits']
SKIP_LIST['SKIP_SHAPE'] = [cal_shape_spirou, inexts, outexts]

# ff
inexts, outexts = ['f_pp.fits'], ['f_pp_flat_AB.fits']
SKIP_LIST['SKIP_FF'] = [cal_FF_RAW_spirou, inexts, outexts]

# thermal
inexts, outexts = ['d_pp.fits'], ['d_pp_e2ds_AB.fits']
SKIP_LIST['SKIP_THERMAL'] = [cal_thermal_spirou, inexts, outexts]

# extract
inexts = ['a_pp.fits', 'c_pp.fits', 'd_pp.fits', 'f_pp.fits', 'o_pp.fits']
outexts = ['a_pp_e2ds_AB.fits', 'c_pp_e2ds_AB.fits', 'd_pp_e2ds_AB.fits',
           'f_pp_e2ds_AB.fits', 'o_pp_e2ds_AB.fits']
SKIP_LIST['SKIP_EXTRACT'] = [cal_extract_RAW_spirou, inexts, outexts]

# mk_tellu
inexts = ['o_pp_e2ds_AB.fits', 'o_pp_e2dsff_AB.fits']
outexts = ['o_pp_e2ds_AB_trans.fits', 'o_pp_e2dsff_AB_trans.fits']
SKIP_LIST['SKIP_MK_TELLU '] = [obj_mk_tellu_new, inexts, outexts]

# fit_tellu
inexts = ['o_pp_e2ds_AB.fits', 'o_pp_e2dsff_AB.fits']
outexts = ['o_pp_e2ds_AB_tellu_corrected.fits',
           'o_pp_e2dsff_AB_tellu_corrected.fits']
SKIP_LIST['SKIP_FIT_TELLU'] = [obj_fit_tellu, inexts, outexts]


# -----------------------------------------------------------------------------
# define the key to identify runs in config file
RUN_KEY = 'ID'
# column names for run tables
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
    # sort out which mode we are in
    if 'ALL' in runtable.values():
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
    run_objects = check_runlist(params, tables, paths, run_objects, keylist)

    # return run objects
    return run_objects


def check_runlist(params, tables, paths, runlist, keylist):

    out_runlist = []

    for it, run_item in enumerate(runlist):
        # ------------------------------------------------------------------
        # check that we want to run this recipe
        check = check_run_params(params, run_item)
        # ------------------------------------------------------------------
        # for remaining arguments if they are fits file check that they are
        #   valid (i.e. that they are in tables)
        check_fits_files(params, it, run_item, keylist, tables, paths)
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

    pass





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


def check_fits_files(params, it, run_item, keylist, tables, paths):

    recipe, nightname = run_item.recipename, run_item.nightname
    kind = run_item.kind
    args, start = run_item.args, run_item.argstart
    # get the table and path
    rtable, rpath = tables[kind], paths[kind]

    # ------------------------------------------------------------------
    # for remaining arguments if they are fits file check that they are
    #   valid (i.e. that they are in tables)
    for arg in args[start:]:
        # skip wildcard arguments if allowed
        if recipe in ALLOW_WILDCARDS:
            if '*' in arg:
                continue
        # must be fits files
        if arg.endswith('.fits'):
            # get absolute path
            if nightname != '':
                abspath = os.path.join(rpath, nightname, arg)
            else:
                abspath = None
            # check night name in rtable
            if nightname != '' and nightname not in rtable[NIGHT_COL]:
                # log error
                eargs = [recipe, RUN_KEY, keylist[it], run_item]
                emsg1 = ('RunList Error: Night name "{0}" invalid'
                         ''.format(nightname))
                emsg2 = '\t Line: {1}{2} = {3}'.format(*eargs)
                WLOG(params, 'error', [emsg1, emsg2])
            # check arg (filename) in rtable
            if abspath is not None and abspath not in rtable[ABSFILE_COL]:
                # log error
                eargs = [recipe, RUN_KEY, keylist[it], run_item]
                emsg1 = ('RunList Error: Filename {0} not '
                         'found'.format(abspath))
                emsg2 = '\t Line: {1}{2} = {3}'.format(*eargs)
                WLOG(params, 'error', [emsg1, emsg2])


def check_run_params(params, run_item):

    # check run list
    for key in RUN_LIST:
        rl_item = RUN_LIST[key]
        # check if recipe names agree
        cond1 = run_item.recipename == remove_py(rl_item.__NAME__)
        # check if key in params
        cond2 = key in params
        # if both conditions met then we take the condition from params
        if cond1 and cond2:
            return params[key]
        # if we don't have key in params and key isn't in RUN_LIST we should
        #   just pass
        elif not (cond1 and cond2):
            return True
    # if we get to here then check has failed
    return False


# =============================================================================
# End of code
# =============================================================================
